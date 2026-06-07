# Stage 1: Build the React Application
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Pass in the backend URL dynamically at build time (defaults to localhost)
ARG VITE_API_URL="http://127.0.0.1:8000"
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve with Nginx for production-grade static hosting
FROM nginx:alpine
# Copy the built Vite assets to Nginx's default public folder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose standard HTTP port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
