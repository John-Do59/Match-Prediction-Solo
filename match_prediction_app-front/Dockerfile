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

# Copie de la configuration Nginx unique
COPY match_prediction_app-front/nginx.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers compilés depuis l'étape précédente
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Ajustement des permissions
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid /var/cache/nginx /var/log/nginx /etc/nginx/conf.d

USER nginx

# Exposition du port (Non-privileged)
EXPOSE 8080

# Lancement de Nginx
CMD ["nginx", "-g", "daemon off;"]

