from fastapi import APIRouter, Depends, HTTPException, status
import httpx
import requests
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

from ..database import get_db
from ..schemas.prediction import PredictionRequest, PredictionResponse
from ..schemas.user import PredictionHistoryOut
from ..routes.auth import get_current_user
from ..models.user import User, PredictionHistory
from ..models.team import Team
from ..core.config import settings
from ..utils.team_mapper import normalize_team

router = APIRouter(prefix="/predictions", tags=["Predictions"])

LFP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.4 Safari/605.1.15",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://ligue1.com",
    "Referer": "https://ligue1.com/",
    "application": "ligue1",
    "client-language": "fr-FR",
    "platform": "web",
}

FINISHED_STATES = {"finished", "termine", "terminé", "played"}


def _extract_results_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    results = raw.get("results", {})
    if isinstance(results, dict):
        if "matches" in results and isinstance(results["matches"], dict):
            return results["matches"]
        merged: Dict[str, Any] = {}
        for item in results.values():
            if isinstance(item, dict) and isinstance(item.get("matches"), dict):
                merged.update(item["matches"])
        return merged
    if isinstance(results, list):
        merged = {}
        for item in results:
            if isinstance(item, dict) and isinstance(item.get("matches"), dict):
                merged.update(item["matches"])
        return merged
    return {}


def _parse_score(match: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
    for key in ("score", "scores", "result", "results"):
        score = match.get(key)
        if isinstance(score, dict):
            for home_key, away_key in (("home", "away"), ("homeScore", "awayScore"), ("home_goals", "away_goals")):
                if home_key in score and away_key in score:
                    try:
                        return int(score[home_key]), int(score[away_key])
                    except (TypeError, ValueError):
                        pass
    for container_name in ("home", "away"):
        side = match.get(container_name, {})
        if isinstance(side, dict):
            candidate_key = "score"
            if candidate_key in side:
                try:
                    current = int(side[candidate_key])
                    other = int(match["away" if container_name == "home" else "home"][candidate_key])
                    return (current, other) if container_name == "home" else (other, current)
                except (TypeError, ValueError, KeyError):
                    pass
    return None, None


def _fetch_finished_matches(gameweek: Optional[int]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    # L'API LFP limite daysLimit a 14 maximum
    url = "https://ma-api.ligue1.fr/championships-daily-calendars/matches?timezone=Europe/Paris&daysLimit=14&lookAfter=false"
    response = requests.get(url, headers=LFP_HEADERS, timeout=15.0)
    response.raise_for_status()
    matches_dict = _extract_results_dict(response.json())

    indexed_results: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for match in matches_dict.values():
        if not isinstance(match, dict):
            continue

        gw = match.get("gameWeekNumber")
        if gameweek is not None and str(gw) != str(gameweek):
            continue

        home_name = (((match.get("home") or {}).get("clubIdentity") or {}).get("name") or "").strip()
        away_name = (((match.get("away") or {}).get("clubIdentity") or {}).get("name") or "").strip()
        if not home_name or not away_name:
            continue

        home_goals, away_goals = _parse_score(match)
        state_name = str((match.get("matchState") or {}).get("name", "")).strip().lower()
        state_name = state_name.replace("é", "e")
        has_score = home_goals is not None and away_goals is not None
        is_finished = state_name in FINISHED_STATES or has_score
        if not is_finished or not has_score:
            continue

        if home_goals > away_goals:
            actual_result = "HOME_WIN"
        elif away_goals > home_goals:
            actual_result = "AWAY_WIN"
        else:
            actual_result = "DRAW"

        key = (normalize_team(home_name).lower(), normalize_team(away_name).lower())
        indexed_results[key] = {
            "actual_result": actual_result,
            "actual_home_goals": home_goals,
            "actual_away_goals": away_goals,
            "gameweek": gw,
        }
    return indexed_results


def _fetch_live_probabilities(home_team: str, away_team: str, season: str) -> Optional[Dict[str, float]]:
    try:
        response = requests.post(
            f"{settings.ML_API_URL}/predict",
            json={
                "home_team": home_team,
                "away_team": away_team,
                "season": season,
            },
            headers={"X-Service-Token": settings.SERVICE_TOKEN},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        probs = data.get("probabilities", {})
        home_prob = float(probs.get("HOME", 0.0))
        draw_prob = float(probs.get("DRAW", 0.0))
        away_prob = float(probs.get("AWAY", 0.0))
        return {"HOME_WIN": home_prob, "DRAW": draw_prob, "AWAY_WIN": away_prob}
    except Exception:
        return None


def _compute_proximity(actual_result: Optional[str], probs_map: Optional[Dict[str, float]]) -> Dict[str, Any]:
    if not actual_result or not probs_map:
        return {
            "probability_actual_result": None,
            "proximity_score": None,
            "proximity_status": "unknown",
        }
    actual_prob = float(probs_map.get(actual_result, 0.0))
    score = round(actual_prob * 100, 1)
    if score >= 45:
        status = "good"
    elif score >= 30:
        status = "close"
    else:
        status = "poor"
    return {
        "probability_actual_result": score,
        "proximity_score": score,
        "proximity_status": status,
    }


# ─────────────────────────────────────────────
# GET /predictions/teams
# Liste les équipes disponibles (depuis la BDD App)
# ─────────────────────────────────────────────
@router.get("/teams")
def get_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).order_by(Team.name).all()
    return [{"id": team.id, "name": team.name, "logo_url": team.logo_url} for team in teams]


# ─────────────────────────────────────────────
# POST /predictions/predict
# Proxy vers l'API ML (port 8001) + sauvegarde historique
# ─────────────────────────────────────────────
class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    season: Optional[str] = "2024/2025"


@router.post("/predict")
async def predict_match(
    data: PredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Proxy la requête vers l'API ML et sauvegarde le résultat dans l'historique.
    """
    # 1. Résolution des équipes en BDD (pour obtenir id et logo)
    home_team = db.query(Team).filter(Team.name == data.home_team).first()
    away_team = db.query(Team).filter(Team.name == data.away_team).first()

    if not home_team or not away_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Une ou les deux équipes sont introuvables dans la base de données.",
        )

    # 2. Appel au service ML
    ml_url = f"{settings.ML_API_URL}/predict"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                ml_url,
                json={
                    "home_team": data.home_team,
                    "away_team": data.away_team,
                    "season": data.season,
                },
                headers={"X-Service-Token": settings.SERVICE_TOKEN},
            )
        response.raise_for_status()
        ml_result = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Erreur retournée par le service ML : {exc.response.text}",
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service ML inaccessible ({settings.ML_API_URL}) : {exc}",
        )

    # 3. Extraction des résultats ML
    predicted_result = ml_result.get("predicted_result") or ml_result.get("prediction")
    confidence_score = ml_result.get("confidence") or ml_result.get("confidence_score")

    # 4. Sauvegarde dans l'historique (modèle hybride : IDs + logos)
    history_entry = PredictionHistory(
        user_id=current_user.id,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        home_team_name=home_team.name,
        home_team_logo_url=home_team.logo_url,
        away_team_name=away_team.name,
        away_team_logo_url=away_team.logo_url,
        predicted_result=str(predicted_result) if predicted_result is not None else None,
        confidence_score=float(confidence_score) if confidence_score is not None else None,
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)

    # 5. Retour enrichi avec logos
    return {
        **ml_result,
        "home_team_logo_url": home_team.logo_url,
        "away_team_logo_url": away_team.logo_url,
    }


# ─────────────────────────────────────────────
# GET /predictions/history
# Historique des prédictions de l'utilisateur courant
# ─────────────────────────────────────────────
@router.get("/history", response_model=List[PredictionHistoryOut])
def get_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    gameweek: Optional[int] = None,
    include_live_results: bool = False,
    include_proximity: bool = False,
    season: str = "2025",
):
    rows = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .limit(limit)
        .all()
    )

    if not include_live_results:
        return rows

    try:
        live_results = _fetch_finished_matches(gameweek=gameweek)
    except Exception:
        # fallback silencieux: on renvoie l'historique sans enrichissement si l'API externe est indisponible
        return rows

    enriched_rows = []
    for row in rows:
        payload = PredictionHistoryOut.model_validate(row).model_dump()
        key = (
            normalize_team((row.home_team_name or "")).lower(),
            normalize_team((row.away_team_name or "")).lower(),
        )
        live = live_results.get(key)
        if live:
            payload.update(live)
            payload["is_correct"] = row.predicted_result == live["actual_result"]
        else:
            payload["actual_result"] = None
            payload["actual_home_goals"] = None
            payload["actual_away_goals"] = None
            payload["gameweek"] = None
            payload["is_correct"] = None

        if include_proximity:
            probs_map = _fetch_live_probabilities(
                home_team=row.home_team_name,
                away_team=row.away_team_name,
                season=season,
            )
            payload.update(_compute_proximity(payload.get("actual_result"), probs_map))
        else:
            payload["probability_actual_result"] = None
            payload["proximity_score"] = None
            payload["proximity_status"] = "unknown"
        enriched_rows.append(payload)

    return enriched_rows


# ─────────────────────────────────────────────
# POST /predictions/history  (save manuel — optionnel)
# ─────────────────────────────────────────────
class PredictionHistoryCreate(BaseModel):
    home_team_name: str
    home_team_logo_url: Optional[str] = None
    away_team_name: str
    away_team_logo_url: Optional[str] = None
    predicted_result: str
    confidence_score: float


@router.post("/history", response_model=PredictionHistoryOut)
def save_prediction_history(
    data: PredictionHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Résolution optionnelle des IDs à partir des noms
    home_team = db.query(Team).filter(Team.name == data.home_team_name).first()
    away_team = db.query(Team).filter(Team.name == data.away_team_name).first()

    new_prediction = PredictionHistory(
        user_id=current_user.id,
        home_team_id=home_team.id if home_team else None,
        away_team_id=away_team.id if away_team else None,
        home_team_name=data.home_team_name,
        home_team_logo_url=data.home_team_logo_url or (home_team.logo_url if home_team else None),
        away_team_name=data.away_team_name,
        away_team_logo_url=data.away_team_logo_url or (away_team.logo_url if away_team else None),
        predicted_result=data.predicted_result,
        confidence_score=data.confidence_score,
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    return new_prediction


def register_routes(app):
    app.include_router(router)
