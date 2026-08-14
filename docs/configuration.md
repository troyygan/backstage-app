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
```

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
