# Build context is the web/ directory. The deploy step syncs the courseware
# module markdown into web/content/modules before building so the static pages
# can be generated at build time.

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine AS run
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8080
ENV HOSTNAME=0.0.0.0

COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public

# OpenShift runs containers with an arbitrary non-root UID in the root group.
RUN chgrp -R 0 /app && chmod -R g=u /app

EXPOSE 8080
USER 1001
CMD ["node", "server.js"]
