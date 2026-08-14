# Catalog model

The Backstage catalog is populated from `catalog-info.yaml` files. For this
homelab, entities live in three places:

| Location | Entities |
|---|---|
| `homelab-workloads/stacks/<app>/catalog-info.yaml` | One `Component` per deployed service (settlnz, monitoring, registry, traefik, uptime-kuma, postgres, minio, loki) |
| `homelab-workloads/catalog-info.yaml` | The workloads repo itself |
| `homelab-platform/catalog-info.yaml` | The platform repo |
| `backstage-app/catalog-info.yaml` | This portal itself (dogfooding) |

## Entity kinds

- **`Component`** (`type: service`) — a deployed workload stack.
- **`Component`** (`type: other`) — an IaC / deploy repo.

## Conventions

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: <kebab-case, e.g. settlnz>
  description: <one line>
  annotations:
    github.com/project-slug: <owner>/<repo>
    backstage.io/techdocs-ref: dir:.   # points at that repo's docs/ (via mkdocs.yml)
spec:
  type: service
  owner: user:troyygan
  lifecycle: production
  system: homelab
```

Rules applied across this homelab:

- `owner: user:troyygan` — single-operator homelab.
- `lifecycle: production` for core stacks, `experimental` for dev/POC items.
- `backstage.io/techdocs-ref: dir:.` on any entity whose repo has an `mkdocs.yml`
  + `docs/` folder.
- `system: homelab` groups all entities under one umbrella in the catalog UI.

## Catalog discovery

`troyygan` is a **personal GitHub account**, not an organization, so GitHub
**org discovery does not apply**. The catalog is populated via **explicit URL
locations** configured in `app-config.production.yaml`:

```yaml
catalog:
  locations:
    - type: url
      target: https://github.com/troyygan/homelab-workloads/blob/main/catalog-info.yaml
    - type: url
      target: https://github.com/troyygan/homelab-platform/blob/main/catalog-info.yaml
    - type: url
      target: https://github.com/troyygan/backstage-app/blob/main/catalog-info.yaml
```

Each `catalog-info.yaml` may reference further entities via `catalog: locations`
in the repo (e.g. per-stack entities), or the root file can list them inline.
