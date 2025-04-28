# --- Build Stage ---
FROM node:18-alpine AS builder
WORKDIR /app

# copy lockfile + manifest
COPY package.json package-lock.json ./

# install exact deps
RUN npm ci

# copy rest of source, then build
COPY . .
RUN npm run build

# --- Serve Stage ---
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

