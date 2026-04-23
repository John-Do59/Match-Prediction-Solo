# Documentation : Mise en place de Let's Encrypt (Production)

Pour passer d'un certificat auto-signé à un certificat valide en production avec Let's Encrypt, suivez cette procédure.

## Prérequis
- Un nom de domaine pointant vers l'IP de votre serveur.
- Les ports 80 et 443 ouverts sur votre pare-feu.

## Méthode recommandée : Certbot (Standalone)

Si vous n'avez pas encore lancé Nginx :

1.  **Installer Certbot** :
    ```bash
    sudo apt-get update
    sudo apt-get install certbot
    ```

2.  **Générer le certificat** :
    ```bash
    sudo certbot certonly --standalone -d votre-domaine.com
    ```

3.  **Localisation des fichiers** :
    Les certificats seront générés dans `/etc/letsencrypt/live/votre-domaine.com/`.
    - Certificat : `fullchain.pem`
    - Clé privée : `privkey.pem`

## Intégration avec notre Docker

Pour utiliser ces certificats avec notre conteneur Nginx sans modifier le code :

1.  **Copier ou lier les certificats** dans le dossier `ssl/` à la racine du projet :
    ```bash
    cp /etc/letsencrypt/live/votre-domaine.com/fullchain.pem ./ssl/
    cp /etc/letsencrypt/live/votre-domaine.com/privkey.pem ./ssl/
    ```

2.  **Relancer l'environnement** :
    ```bash
    ./scripts/run_docker_env.sh
    ```

## Renouvellement automatique

Ajoutez une tâche cron pour renouveler le certificat et copier les fichiers :

```bash
0 0 1 * * certbot renew --post-hook "cp /etc/letsencrypt/live/votre-domaine.com/*.pem /chemin/vers/projet/ssl/ && docker restart frontend-vue"
```

## Note sur Cloudflare
Si vous utilisez Cloudflare, vous pouvez utiliser leurs certificats d'origine (Origin Certificates) et les placer dans le dossier `ssl/`. Cloudflare gérera alors le SSL entre le visiteur et leurs serveurs, et notre Nginx gérera le SSL entre Cloudflare et votre serveur.
