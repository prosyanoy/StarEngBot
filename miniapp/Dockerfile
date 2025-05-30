# ─── Stage 1: build the app ───
FROM node:18-alpine AS builder
WORKDIR /app

# 1) Copy manifests & install
COPY package.json package-lock.json ./
RUN npm ci

# 2) Copy source & build
COPY . .
RUN npm run build

# ─── Stage 2: serve with nginx ───
FROM nginx:stable-alpine
# Your custom nginx.conf if you have one
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the build output into nginx’s html dir
# Vite outputs to /app/dist by default
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
