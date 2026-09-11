# syntax=docker/dockerfile:1
# Adapted from docker init; the runtime contains only Nitro's standalone output.
FROM node@sha256:2fe369e969550cde8e867afc3fe370b260140cab4a23d467074295b42163d553 AS base
WORKDIR /app

FROM base AS build
COPY package.json /tmp/kollio-package.json
RUN npm install --global "$(node -p "require('/tmp/kollio-package.json').packageManager.split('+')[0]")"
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages packages
COPY apps/web apps/web
ARG NUXT_PUBLIC_AUTH_ENABLED=false
ENV NUXT_PUBLIC_AUTH_ENABLED=$NUXT_PUBLIC_AUTH_ENABLED
RUN --mount=type=cache,target=/root/.local/share/pnpm/store pnpm install --frozen-lockfile
RUN pnpm --dir apps/web build

FROM base AS final
ENV NODE_ENV=production HOST=0.0.0.0 PORT=3000
COPY --from=build --chown=node:node /app/apps/web/.output ./.output
USER node
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
