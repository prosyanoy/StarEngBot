# --- Build Stage ---
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source & build
COPY . .
RUN npm run build

# --- Production Stage ---
FROM nginx:stable-alpine
# Copy built files to nginx’s public folder
COPY --from=builder /app/build /usr/share/nginx/html

# (Optional) Add a basic nginx config if you need SPA fallback:
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

