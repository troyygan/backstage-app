# backstage-app

The Troyygan homelab **developer portal** — a [Backstage](https://backstage.io)
instance (v1.53) providing a **software catalog** of everything running in the
homelab plus **TechDocs** rendered from each repo's `docs/` folder.

This is a **source repo**: CI builds the Docker image and pushes it to the local
registry (`registry.homelab.lan:5000/backstage:<sha>`). The deployment manifest
lives in `homelab-workloads/stacks/backstage/`.

> Deploy runbook: `homelab-workloads/docs/runbooks/backstage-bootstrap.md`.
> Entity conventions: `homelab-workloads/docs/catalog-model.md`.

## What it does

- **Software Catalog** (`/`) — lists every homelab service as a `Component`
  entity, read from `catalog-info.yaml` files in `homelab-workloads`,
  `homelab-platform`, and this repo.
- **TechDocs** — renders existing markdown `docs/` folders (via `mkdocs.yml` +
  `backstage.io/techdocs-ref` annotations).
- **Search** — Postgres-backed search over catalog + docs.
- **Guest auth** — LAN-only eval; GitHub SSO is a future step (the
  `github-provider` module is already wired in `packages/backend/src/index.ts`).

## Repository layout

```
app-config.yaml              # base config (dev defaults, env-injected URLs)
app-config.production.yaml   # prod: Postgres, GitHub locations, guest auth
packages/app/                # frontend
packages/backend/            # backend + Dockerfile (bundle embeds the frontend)
packages/backend/src/index.ts# plugin wiring
catalog-info.yaml            # this repo's own catalog entity (dogfooding)
.github/workflows/backstage-ci.yml  # build + push to local registry
examples/                    # scaffold demo data (dev only)
```

## Local development

Requires Node 22+ (Yarn 4 is pinned via `packageManager`).

```sh
yarn install
yarn dev          # frontend on :3000, backend on :7007
```

Local dev uses in-memory sqlite + the `examples/` catalog. Production config is
env-driven (see below).

## Environment variables

| Var | Required | Purpose |
|---|---|---|
| `BACKSTAGE_APP_URL` | yes (prod) | Browser-facing base URL (dev: `https://192.168.1.30:7007`, core: `https://backstage.homelab.lan`). Drives `app.baseUrl`, `backend.baseUrl`, and `cors.origin`. |
| `BACKSTAGE_HTTPS` | core only | `false` on core (Traefik terminates TLS; Backstage serves plain HTTP internally). Unset/`true` elsewhere (direct HTTPS). |
| `POSTGRES_HOST` | prod | `192.168.1.32` (docker-data-01) |
| `POSTGRES_PORT` | prod | `5432` |
| `POSTGRES_USER` | prod | `backstage` (DB user) |
| `POSTGRES_PASSWORD` | prod | `backstage` DB password — **never committed** |
| `GITHUB_TOKEN` | prod | PAT with `repo` scope for catalog fetches + TechDocs cloning |

Set these in **Portainer → stack → env vars**, never in Git.

## Image build (CI)

`.github/workflows/backstage-ci.yml` runs on the **self-hosted LAN runner**
(`[self-hosted, linux, homelab]`) because the registry is LAN-only:

1. `yarn install --immutable`
2. `yarn tsc` + `yarn build:backend` (backend bundle embeds the frontend)
3. `docker build` → `registry.homelab.lan:5000/backstage:${GITHUB_SHA::12}`
4. Push SHA tag + `latest`, optionally trigger the Portainer webhook.

> The image build is heavy (`yarn workspaces focus --production`). Allow a long
> first run; layer caching helps on subsequent pushes.

## Config reference

- Catalog locations → `app-config.production.yaml` (`catalog.locations`,
  explicit URLs per repo — `troyygan` is a personal account, so GitHub **org**
  discovery does not apply).
- GitHub token → `app-config.yaml` (`integrations.github`).
- TechDocs → `app-config.yaml`: `builder: local`, `runIn: docker` (requires the
  Docker socket mounted into the container — see the stack compose files).
