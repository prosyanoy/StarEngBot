# --- Build Stage ---
FROM node:18-alpine AS builder
WORKDIR /app

# copy lockfile + manifest
COPY package.json package-lock.json ./

# install exact deps
COPY . .
RUN npm ci && run build


# --- Serve Stage ---
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

