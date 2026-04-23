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

# Copie de la configuration Nginx (crucial pour Vue Router)
COPY match_prediction_app-front/nginx.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers compilés depuis l'étape précédente
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Ajustement des permissions pour permettre à l'utilisateur 'nginx' (non-root) de tourner
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid /var/cache/nginx /var/log/nginx

USER nginx

# Exposition des ports (Non-privileged)
EXPOSE 8080 8443

# Création du dossier pour les certificats SSL avec les bonnes permissions
RUN mkdir -p /etc/nginx/ssl && chown -R nginx:nginx /etc/nginx/ssl

# Nginx démarre automatiquement par défaut
CMD ["nginx", "-g", "daemon off;"]

