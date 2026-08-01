import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  site: 'https://scc.github.io',
  base: '/scc-blog',
  integrations: [mdx()],
});
