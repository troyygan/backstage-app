# ${{ values.name }}

${{ values.description }}

Scaffolded from the Backstage "New Homelab Service" template. Deploy via the
`homelab-workloads` repo (Portainer GitOps) — see `stacks/${{ values.name }}/`.

## Local development

```sh
npm install
npm start          # http://localhost:3000
```

## CI

A push to `main` builds the Docker image and pushes `registry.homelab.lan:5000/${{ values.name }}`
(SHA + `latest`) on the homelab self-hosted runner.
