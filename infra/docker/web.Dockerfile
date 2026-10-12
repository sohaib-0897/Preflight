FROM node:22.23.3-alpine AS dependencies
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci

FROM dependencies AS build
ARG PREFLIGHT_API_ORIGIN=http://api:8000
ENV PREFLIGHT_API_ORIGIN=$PREFLIGHT_API_ORIGIN NEXT_TELEMETRY_DISABLED=1
COPY apps/web/ ./
RUN npm run build

FROM node:22.23.3-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
RUN addgroup -g 10001 preflight && adduser -D -u 10001 -G preflight preflight
COPY --from=build --chown=10001:10001 /app/.next/standalone ./
COPY --from=build --chown=10001:10001 /app/.next/static ./.next/static
COPY --from=build --chown=10001:10001 /app/public ./public
RUN mkdir -p /app/.next/cache && chown 10001:10001 /app/.next/cache
USER 10001:10001
EXPOSE 3000
CMD ["node", "server.js"]
