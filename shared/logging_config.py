"""
Configuration partagée du système de logging pour les microservices.

Ce module fournit une configuration de logging flexible qui s'adapte à l'environnement :
- En développement : Sortie colorée et lisible sur la console.
- En production : Sortie au format JSON pour une intégration facile avec les systèmes de collecte de logs (ELK, CloudWatch, etc.).

L'utilisation principale se fait via la fonction `setup_logging(service_name)`.
"""
import logging
import sys
import os
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """
    Formateur de logs au format JSON pour la production.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Ajout des metadata additionnelles (extra)
        if hasattr(record, "extra"):
            log_record.update(record.extra)
            
        return json.dumps(log_record)

def setup_logging(service_name: str):
    """
    Configure le logging pour un service donné.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    is_production = os.getenv("ENV", "development").lower() == "production"
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Nettoyage des handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    handler = logging.StreamHandler(sys.stdout)
    
    if is_production:
        # En production, on utilise le format JSON
        handler.setFormatter(JsonFormatter())
    else:
        # En développement, on utilise un format lisible avec couleurs
        fmt = f"\033[0;34m%(asctime)s\033[0m | \033[0;32m{service_name}\033[0m | %(levelname)s | %(message)s"
        handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))
    
    logger.addHandler(handler)
    
    # Réduire le bruit des bibliothèques tierces
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logger
