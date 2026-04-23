#!/bin/bash

# Script de génération de certificats SSL auto-signés pour le développement local.
# Les certificats seront stockés dans un répertoire local 'ssl' qui sera monté
# dans le conteneur Nginx.

set -e

SSL_DIR="./ssl"
DOMAIN="localhost"

mkdir -p "$SSL_DIR"

echo "--- Génération de certificats SSL auto-signés pour $DOMAIN ---"

# 1. Générer la clé privée de l'autorité de certification (CA)
if [ ! -f "$SSL_DIR/ca.key" ]; then
    openssl genrsa -out "$SSL_DIR/ca.key" 2048
fi

# 2. Générer le certificat de l'autorité de certification (CA)
if [ ! -f "$SSL_DIR/ca.crt" ]; then
    openssl req -x509 -new -nodes -key "$SSL_DIR/ca.key" -sha256 -days 1825 \
        -out "$SSL_DIR/ca.crt" \
        -subj "/C=FR/ST=Paris/L=Paris/O=Match Prediction/CN=Match Prediction Root CA"
fi

# 3. Générer la clé privée du certificat serveur
openssl genrsa -out "$SSL_DIR/privkey.pem" 2048

# 4. Créer le fichier de configuration pour les extensions (SAN)
cat > "$SSL_DIR/openssl.cnf" <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = FR
ST = Paris
L = Paris
O = Match Prediction
CN = $DOMAIN

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = localhost
IP.1 = 127.0.0.1
EOF

# 5. Générer la demande de signature de certificat (CSR)
openssl req -new -key "$SSL_DIR/privkey.pem" -out "$SSL_DIR/server.csr" -config "$SSL_DIR/openssl.cnf"

# 6. Signer le certificat avec notre CA
openssl x509 -req -in "$SSL_DIR/server.csr" -CA "$SSL_DIR/ca.crt" -CAkey "$SSL_DIR/ca.key" \
    -CAcreateserial -out "$SSL_DIR/fullchain.pem" -days 825 -sha256 -extensions v3_req -extfile "$SSL_DIR/openssl.cnf"

# 7. Nettoyage
rm "$SSL_DIR/server.csr" "$SSL_DIR/openssl.cnf"

echo "--- Terminé ---"
echo "Certificats générés dans le dossier : $SSL_DIR"
echo "  - Clé privée : $SSL_DIR/privkey.pem"
echo "  - Certificat (chaîne complète) : $SSL_DIR/fullchain.pem"
echo "IMPORTANT : Pour éviter les alertes de sécurité dans votre navigateur,"
echo "vous pouvez importer $SSL_DIR/ca.crt dans le trousseau d'accès (Mac) ou les paramètres de votre navigateur."
