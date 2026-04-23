from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ..database import get_db
from ..models.user import User, UserFavoriteTeam, PredictionHistory
from ..schemas.user import (
    UserRegister, UserLogin, UserOut, Token, TokenData, 
    UserUpdate, PasswordChange, ForgotPassword, ResetPassword,
    UserStats, UserFavoriteTeamOut, UserFavoriteTeamBase
)
from ..services.auth_service import AuthService
from ..core.config import settings
from ..core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return AuthService.create_user_token(user)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return AuthService.update_user_profile(db, current_user, update_data.model_dump(exclude_unset=True))


@router.delete("/me")
def delete_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    AuthService.delete_user_account(db, current_user)
    return {"message": "Compte supprimé"}


@router.post("/change-password")
def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    AuthService.change_user_password(db, current_user, data.old_password, data.new_password)
    return {"message": "Mot de passe modifié"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    return AuthService.forgot_password(db, data.email)


@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    AuthService.reset_password_with_token(db, data.token, data.new_password)
    return {"message": "Mot de passe réinitialisé"}


# ── Statistiques et Favoris ──────────────────────────────────

@router.get("/me/stats", response_model=UserStats)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_preds = db.query(PredictionHistory).filter(PredictionHistory.user_id == current_user.id).count()
    fav_teams_count = db.query(UserFavoriteTeam).filter(UserFavoriteTeam.user_id == current_user.id).count()
    return {
        "total_predictions": total_preds,
        "favorite_teams_count": fav_teams_count
    }


@router.get("/me/favorites", response_model=List[UserFavoriteTeamOut])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(UserFavoriteTeam).filter(UserFavoriteTeam.user_id == current_user.id).all()


@router.post("/me/favorites", response_model=UserFavoriteTeamOut)
def add_favorite(
    data: UserFavoriteTeamBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if already exists
    existing = db.query(UserFavoriteTeam).filter(
        UserFavoriteTeam.user_id == current_user.id,
        UserFavoriteTeam.team_id == data.team_id
    ).first()
    if existing:
        return existing
        
    new_fav = UserFavoriteTeam(user_id=current_user.id, team_id=data.team_id)
    db.add(new_fav)
    db.commit()
    db.refresh(new_fav)
    return new_fav


@router.delete("/me/favorites/{team_id}")
def remove_favorite(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    fav = db.query(UserFavoriteTeam).filter(
        UserFavoriteTeam.user_id == current_user.id,
        UserFavoriteTeam.team_id == team_id
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
    db.delete(fav)
    db.commit()
    return {"message": "Favori supprimé"}
