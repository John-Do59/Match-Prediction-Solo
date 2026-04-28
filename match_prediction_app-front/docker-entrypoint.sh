#!/bin/sh
set -e

echo "Démarrage du Frontend en mode: ${ENV:-prod}"

if [ "$ENV" = "dev" ]; then
    echo "Utilisation de la configuration HTTP (DEV)"
    cp /etc/nginx/nginx.dev.conf /etc/nginx/conf.d/default.conf
else
    echo "Utilisation de la configuration HTTPS (PROD)"
    if [ ! -f /etc/nginx/ssl/fullchain.pem ]; then
        echo "Erreur: Certificats SSL manquants pour le mode PROD !"
        exit 1
    fi
    cp /etc/nginx/nginx.prod.conf /etc/nginx/conf.d/default.conf
fi

exec nginx -g "daemon off;"
