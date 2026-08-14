# Multi-stage build for the Backstage backend image.
# Everything (yarn install / tsc / build:backend) happens INSIDE Docker, so the
# CI runner only needs `docker build` — no Node.js installed on the host. This
# matches the settlnz pattern (self-hosted runner = docker build + push only).
#
# Executed with the repo root as the docker context:
#   docker build -f packages/backend/Dockerfile -t registry.homelab.lan:5000/backstage:<sha> .
#
# Inspired by the official multi-stage Dockerfile documented at
# https://backstage.io/docs/deployment/docker#multi-stage-build

# ---------------------------------------------------------------- build stage
FROM node:24-trixie-slim AS build

# isolate-vm (scaffolder), sqlite3, pg native deps
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends python3 g++ build-essential libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# The scaffold's .yarnrc.yml pins yarn 4.13.0 via yarnPath (.yarn/releases), so
# no corepack/global yarn is needed — yarn resolves from the repo itself.
COPY --chown=node:node . .

USER node

RUN yarn install --immutable

# tsc outputs type definitions to dist-types/ in the repo root, consumed by the build
RUN yarn tsc

# Build the backend bundle (embeds the frontend) into packages/backend/dist.
RUN yarn build:backend

# ------------------------------------------------------------------ runtime stage
FROM node:24-trixie-slim

# isolate-vm + sqlite3 runtime deps (same as build stage)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends python3 g++ build-essential libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

# This switches many Node.js dependencies to production mode.
ENV NODE_ENV=production
# Disables node snapshot for the Scaffolder (matches the upstream Dockerfile).
ENV NODE_OPTIONS="--no-node-snapshot"

# From here on we use the least-privileged `node` user to run the backend.
USER node

WORKDIR /app

# Copy yarn 4 (pinned in the repo) + workspace manifest so `yarn workspaces focus`
# can install production deps. The skeleton.tar.gz holds each package's package.json.
COPY --chown=node:node .yarn ./.yarn
COPY --chown=node:node .yarnrc.yml ./
COPY --chown=node:node yarn.lock package.json packages/backend/dist/skeleton.tar.gz ./
RUN tar xzf skeleton.tar.gz && rm skeleton.tar.gz

RUN --mount=type=cache,target=/home/node/.cache/yarn,sharing=locked,uid=1000,gid=1000 \
    yarn workspaces focus --all --production && rm -rf "$(yarn cache clean)"

# Then copy the backend bundle + config files.
COPY --chown=node:node packages/backend/dist/bundle.tar.gz app-config.yaml app-config.production.yaml ./
RUN tar xzf bundle.tar.gz && rm bundle.tar.gz

CMD ["node", "packages/backend", "--config", "app-config.yaml", "--config", "app-config.production.yaml"]
