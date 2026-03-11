# Stage 1: Build
FROM node:24-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Pass build-time environment variables
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Stage 2: We just need to build the files, Nginx container will serve them
# We use a tiny alpine image just to hold the volume
FROM alpine:latest as production-stage
COPY --from=build-stage /app/dist /app/dist
CMD ["tail", "-f", "/dev/null"]
