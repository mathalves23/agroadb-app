#!/bin/bash
# Script de Setup SSL com Let's Encrypt

set -e

DOMAIN="${1:-app.agroadb.com}"
EMAIL="${2:-admin@agroadb.com}"

echo "🔐 Configurando SSL para: $DOMAIN"
echo "📧 Email: $EMAIL"

# Instalar certbot
if ! command -v certbot &> /dev/null; then
    echo "📦 Instalando Certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Obter certificado
echo "🔄 Obtendo certificado SSL..."
sudo certbot certonly \
    --nginx \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --domains $DOMAIN

# Copiar certificados para o diretório do projeto
SSL_DIR="./ssl"
mkdir -p $SSL_DIR

sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/
sudo chmod 644 $SSL_DIR/*.pem

echo "✅ Certificado SSL configurado!"
echo "📁 Certificados copiados para: $SSL_DIR"

# Configurar renovação automática
echo "🔄 Configurando renovação automática..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "✅ Renovação automática configurada!"
echo "📅 Certificados serão renovados automaticamente a cada 90 dias"

# Criar script de renovação com hook
cat > /etc/letsencrypt/renewal-hooks/post/deploy-agroadb.sh << 'EOF'
#!/bin/bash
# Hook pós-renovação - Copiar certificados e recarregar nginx

SSL_DIR="/path/to/agroadb/ssl"
DOMAIN="app.agroadb.com"

cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/
chmod 644 $SSL_DIR/*.pem

# Recarregar nginx no docker
docker exec agroadb-nginx nginx -s reload

echo "✅ Certificados atualizados e nginx recarregado"
EOF

sudo chmod +x /etc/letsencrypt/renewal-hooks/post/deploy-agroadb.sh

echo "✅ Script de setup SSL concluído!"
