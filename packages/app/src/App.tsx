import { createApp } from '@backstage/frontend-defaults';
import catalogPlugin from '@backstage/plugin-catalog/alpha';
import techDocsMermaidAddonModule from 'backstage-plugin-techdocs-addon-mermaid/alpha';
import { navModule } from './modules/nav';
import { prometheusModule } from './modules/prometheus';

export default createApp({
  features: [
    catalogPlugin,
    navModule,
    prometheusModule,
    techDocsMermaidAddonModule,
  ],
});
