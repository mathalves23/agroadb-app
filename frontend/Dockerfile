# AgroADB Frontend - Production Docker Image

FROM node:18-alpine AS builder

# Metadados
LABEL maintainer="dev@agroadb.com"

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependências
RUN npm ci --only=production

# Copiar código
COPY . .

# Build
ARG VITE_API_URL=https://api.agroadb.com
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ==================== Production Stage ====================
FROM nginx:alpine

# Copiar build do frontend
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuração do nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
