# Étape 1 : Construction (Build)
FROM node:18-alpine AS build-stage

WORKDIR /app

# Copie des fichiers de configuration node
COPY match_prediction_app-front/package*.json ./

# Installation des dépendances
RUN npm install

# Copie du code source
COPY match_prediction_app-front/ .

# Construction de l'application pour la production
RUN npm run build

# Étape 2 : Serveur de production (Nginx)
FROM nginx:stable-alpine AS production-stage

# Copie des configurations disponibles
COPY match_prediction_app-front/nginx.dev.conf /etc/nginx/nginx.dev.conf
COPY match_prediction_app-front/nginx.prod.conf /etc/nginx/nginx.prod.conf

# Copie du script d'entrée
COPY match_prediction_app-front/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copie des fichiers compilés depuis l'étape précédente
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Ajustement des permissions
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid /var/cache/nginx /var/log/nginx /etc/nginx/conf.d

# Création du dossier pour les certificats SSL avec les bonnes permissions
RUN mkdir -p /etc/nginx/ssl && chown -R nginx:nginx /etc/nginx/ssl

USER nginx

# Exposition des ports (Non-privileged)
EXPOSE 8080 8443

# Utilisation du script d'entrée pour choisir la config au runtime
ENTRYPOINT ["docker-entrypoint.sh"]

