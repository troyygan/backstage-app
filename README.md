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
  `homelab-platform`, `hermes-openclaw-lab`, and this repo.
- **TechDocs** — renders existing markdown `docs/` folders (via `mkdocs.yml` +
  `backstage.io/techdocs-ref` annotations), generated through Docker and published
  to local storage. Mermaid diagrams render through the frontend addon.
- **Search** — Postgres-backed search over catalog + docs.
- **GitHub SSO** — sign in with GitHub (maps to catalog `User` `troyygan` via
  `usernameMatchingUserEntityName`); guest fallback kept for LAN access.

## Repository layout

```
app-config.yaml              # base config (dev defaults, env-injected URLs)
app-config.production.yaml   # prod: Postgres, GitHub SSO, catalog locations
app-config.https.yaml        # https:true (dev) — picked by the Dockerfile CMD
app-config.traefik.yaml      # plain HTTP (core) — picked by the Dockerfile CMD
templates/homelab-service/   # scaffolder template: new own-app source repo
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
| `AUTH_GITHUB_CLIENT_ID` | prod | GitHub OAuth App client ID (sign-in) |
| `AUTH_GITHUB_CLIENT_SECRET` | prod | GitHub OAuth App client secret — **never committed** |
| `BACKSTAGE_MCP_TOKEN` | prod | Static bearer token for the MCP actions endpoint (`/api/mcp-actions/v1`) — **never committed** |

Set these in **Portainer → stack → env vars**, never in Git.

## Image build (CI)

Every push to `main` runs `.github/workflows/backstage-ci.yml` on the **self-hosted LAN runner**
(`[self-hosted, linux, homelab]`) because the registry is LAN-only:

1. Install locked Yarn dependencies, run TypeScript and unit tests, then build the production bundle inside Docker.
2. Publish `registry.homelab.lan:5000/backstage:<full-commit-SHA>` with its OCI revision label. Re-runs verify and reuse that exact image; they never replace a published commit tag.
3. Request the `custom-app-release.yml` workflow in `homelab-workloads` with `target=core`, passing the source run and exact image digest.
4. The workload workflow checks successful source CI and automatically updates the image pin on workload `main`.
5. Portainer CE polling deploys directly to core. Failed source CI leaves core on its previous image. No dev prerequisite or second release PR is needed.

To request optional dev checks, run **Validate, build and deploy Backstage**
manually on `main` with `target: dev`. It validates a temporary dev stack with
its own Postgres and no production integrations, then removes the stack and
its storage. That run never promotes core.

Configure the repository secret `WORKLOADS_DISPATCH_TOKEN` with permission to
run the workload repository's release workflow. Registry authentication stays
in the existing LAN runner Docker configuration. `latest` and a direct
Portainer webhook are no longer part of this release flow. Source pushes and
manual workflow runs both use the same checks.

> The image build is heavy (`yarn workspaces focus --production`). Allow a long
> first run; layer caching helps on subsequent pushes.

## Config reference

- Catalog locations → `app-config.production.yaml` (`catalog.locations`,
  explicit URLs per repo — `troyygan` is a personal account, so GitHub **org**
  discovery does not apply).
- GitHub token → `app-config.yaml` (`integrations.github`).
- TechDocs → `app-config.yaml`: `builder: local`, `runIn: docker` (requires the
  Docker socket mounted into the container — see the stack compose files).
