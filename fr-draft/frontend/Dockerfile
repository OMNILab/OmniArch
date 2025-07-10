# Build stage
FROM registry.cn-hangzhou.aliyuncs.com/lacogito/node:24-alpine3.21 as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application (env.production)
RUN npm run build

# Production stage
FROM registry.cn-hangzhou.aliyuncs.com/lacogito/nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy assets from build stage
COPY --from=build /app/src/assets /usr/share/nginx/html/assets

# Copy nginx configuration if needed
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80
EXPOSE 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 