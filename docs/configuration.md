# Configuration

Backstage reads two config files (per the Dockerfile `CMD`):

1. `app-config.yaml` — base config (dev defaults).
2. `app-config.production.yaml` — production overrides (Postgres, catalog
   locations, guest auth).

## Env-driven values

| Setting | Env var | Notes |
|---|---|---|
| `app.baseUrl` / `backend.baseUrl` / `cors.origin` | `BACKSTAGE_APP_URL` | Must match the browser-facing URL or the frontend can't reach the backend (CORS). |
| `backend.database.connection` | `POSTGRES_HOST` / `POSTGRES_PORT` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Postgres on docker-data-01. |
| `integrations.github.token` | `GITHUB_TOKEN` | PAT with `repo` scope. |

## Postgres

The portal needs the `backstage` database + user on the shared Postgres server
(`192.168.1.32:5432`). Created once:

```sql
CREATE DATABASE backstage;
CREATE USER backstage WITH PASSWORD '<strong-password>';
GRANT ALL PRIVILEGES ON DATABASE backstage TO backstage;
\c backstage
GRANT ALL ON SCHEMA public TO backstage;   -- Postgres 15+
ALTER USER backstage CREATEDB;             -- Backstage creates one database per plugin
```

> **`CREATEDB` is required.** Backstage's Postgres plugin auto-creates a
> database per plugin (catalog, search, techdocs, auth, scaffolder, …). Without
> it, plugins fail at startup with `permission denied to create database`.

## HTTPS

`backend.https: true` generates a **self-signed cert** at startup. HTTPS is
**required** — Backstage's frontend calls `crypto.randomUUID()`, which browsers
only expose in secure contexts. Over plain HTTP on a LAN IP the UI errors with
`globalThis.crypto.randomUUID is not a function`. Expect the browser's
self-signed-cert warning on first visit.

## TechDocs

`app-config.yaml` sets:

```yaml
techdocs:
  builder: 'local'
  generator:
    runIn: 'docker'
  publisher:
    type: 'local'
```

`runIn: docker` means the portal spawns the `spotify/techdocs` container to
generate docs, which requires the Docker socket mounted into the portal
container (see `homelab-workloads/stacks/backstage/docker-compose.yml`).

Mermaid diagrams are rendered in the browser by
`backstage-plugin-techdocs-addon-mermaid`, registered as a TechDocs module in
`packages/app/src/App.tsx`. Documentation repositories can keep their ordinary
`mermaid` code fences and use `techdocs-core` in `mkdocs.yml`; the generator must
provide `mkdocs-techdocs-core` 1.0.2 or later. No external diagram service is used.
See the [Backstage Mermaid guide](https://backstage.io/docs/features/techdocs/how-to-guides/#how-to-add-mermaid-support-in-techdocs)
and the [addon instructions](https://github.com/johanneswuerbach/backstage-plugin-techdocs-addon-mermaid#readme).

The agent learning lab is registered through its explicit GitHub catalog URL in
`app-config.production.yaml`. After the lab catalog and documentation changes
reach its `main` branch and this portal image is rebuilt and deployed, open
`/docs/default/component/hermes-openclaw-lab` and check the roadmap diagrams in
both the TechDocs reader and the catalog entity's Docs tab. A successful MkDocs
build verifies the generated documentation; browser rendering also needs this
frontend addon. The standard TechDocs CLI preview does not include the addon.
