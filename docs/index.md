# backstage-app

This is the **developer portal** for the Troyygan homelab, built on
[Backstage](https://backstage.io). It is one of three artifacts that make up the
homelab platform:

| Artifact | Repo | Responsibility |
|---|---|---|
| Platform provisioning | `homelab-platform` | Proxmox VMs, Docker, Portainer (OpenTofu + Ansible) |
| Deployment manifests | `homelab-workloads` | Docker Compose stacks via Portainer GitOps |
| Developer portal | `backstage-app` (this repo) | Catalog + TechDocs + search over the above |

The portal is deployed as an own-built image
(`registry.homelab.lan:5000/backstage:<sha>`) to `dev` first, then promoted to
`core`. See the runbook in `homelab-workloads/docs/runbooks/backstage-bootstrap.md`.

## What the portal gives you

- **Software Catalog** — every service in the homelab registered as a
  `Component` entity, read live from `catalog-info.yaml` files across the repos.
- **TechDocs** — existing markdown documentation rendered in a searchable UI.
- **Search** — Postgres-backed search across catalog and docs.
