import { createFrontendModule } from '@backstage/frontend-plugin-api';
import { EntityContentBlueprint } from '@backstage/plugin-catalog-react/alpha';
import { isPrometheusAvailable } from '@roadiehq/backstage-plugin-prometheus';

// Adds a "Metrics" tab to catalog entity pages for entities annotated with
// `prometheus.io/scrape: "true"`. Data flows through Backstage's proxy to the
// homelab Prometheus (see app-config.yaml `proxy`).
const prometheusEntityContent = EntityContentBlueprint.make({
  name: 'prometheus',
  params: {
    path: 'metrics',
    title: 'Metrics',
    filter: isPrometheusAvailable,
    loader: () =>
      import('@roadiehq/backstage-plugin-prometheus').then(m => (
        <m.EntityPrometheusContent />
      )),
  },
});

export const prometheusModule = createFrontendModule({
  pluginId: 'catalog',
  extensions: [prometheusEntityContent],
});
