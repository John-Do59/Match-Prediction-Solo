from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialisation du limiteur de débit basé sur l'adresse IP
# Par défaut, on n'applique pas de limite globale, mais on définit l'instance ici.
limiter = Limiter(key_func=get_remote_address)
