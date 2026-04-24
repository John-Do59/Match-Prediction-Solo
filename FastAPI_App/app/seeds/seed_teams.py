import logging
from sqlalchemy.orm import Session
from ..database import SessionLocal, engine
from ..models.team import Team

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
TEAMS_DATA = [
    {"name": "Angers",         "logo_url": "https://brandlogos.net/wp-content/uploads/2022/07/angers_sco-logo_brandlogos.net_1yevi-512x512.png"},
    {"name": "Auxerre",        "logo_url": "https://brandlogos.net/wp-content/uploads/2018/12/aj_auxerre-logo_brandlogos.net_fwi5k-512x512.png"},
    {"name": "Le Havre",       "logo_url": "https://brandlogos.net/wp-content/uploads/2018/12/le_havre_ac-logo_brandlogos.net_yx6ic-512x622.png"},
    {"name": "Lens",           "logo_url": "https://brandlogos.net/wp-content/uploads/2018/12/rc-lens-logo-512x512.png"},
    {"name": "Lille",          "logo_url": "https://brandlogos.net/wp-content/uploads/2021/01/lille-osc-logo-512x512.png"},
    {"name": "Lorient",        "logo_url": "https://brandlogos.net/wp-content/uploads/2018/11/fc_lorient-logo_brandlogos.net_flntm-512x512.png"},
    {"name": "Lyon",           "logo_url": "https://brandlogos.net/wp-content/uploads/2015/03/Olympique-Lyonnais-logo-512x594.png"},
    {"name": "Marseille",      "logo_url": "https://brandlogos.net/wp-content/uploads/2014/12/olympique_de_marseille-logo_brandlogos.net_fnliw-512x657.png"},
    {"name": "Metz",           "logo_url": "https://brandlogos.net/wp-content/uploads/2025/08/fc_metz-logo_brandlogos.net_umt95-512x737.png"},
    {"name": "Monaco",         "logo_url": "https://brandlogos.net/wp-content/uploads/2018/11/AS-Monaco-FC-512x885.png"},
    {"name": "Nantes",         "logo_url": "https://brandlogos.net/wp-content/uploads/2022/07/fc_nantes-logo_brandlogos.net_cawqm-512x512.png"},
    {"name": "Nice",           "logo_url": "https://brandlogos.net/wp-content/uploads/2022/07/ogc_nice-logo_brandlogos.net_1nwir-512x512.png"},
    {"name": "Paris FC",       "logo_url": "https://brandlogos.net/wp-content/uploads/2013/10/paris-fc-1969-vector-logo.png"},
    {"name": "Paris SG",       "logo_url": "https://brandlogos.net/wp-content/uploads/2014/12/paris-saint-germain-logo-512x512.png"},
    {"name": "Rennes",         "logo_url": "https://brandlogos.net/wp-content/uploads/2018/12/stade_rennais_fc-logo_brandlogos.net_eiekb-512x512.png"},
    {"name": "Stade Brestois", "logo_url": "https://brandlogos.net/wp-content/uploads/2022/07/stade_brestois_29-logo_brandlogos.net_llie5-512x512.png"},
    {"name": "Strasbourg",     "logo_url": "https://brandlogos.net/wp-content/uploads/2019/01/rc_strasbourg_alsace-logo_brandlogos.net_sutxm-512x512.png"},
    {"name": "Toulouse",       "logo_url": "https://brandlogos.net/wp-content/uploads/2022/07/toulouse_fc-logo_brandlogos.net_mpshb-512x512.png"}
]

def seed_teams(db: Session):
    logger.info("Début du seeding des équipes...")
    for team_data in TEAMS_DATA:
        # Vérification de l'existence (idempotence)
        exists = db.query(Team).filter(Team.name == team_data["name"]).first()
        if not exists:
            new_team = Team(**team_data)
            db.add(new_team)
            logger.info(f"Ajout de l'équipe : {team_data['name']}")
        else:
            logger.info(f"L'équipe {team_data['name']} existe déjà, passage.")
    
    db.commit()
    logger.info("Seeding des équipes terminé avec succès.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_teams(db)
    except Exception as e:
        logger.error(f"Erreur lors du seeding : {e}")
        db.rollback()
    finally:
        db.close()
