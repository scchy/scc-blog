import mdx from '@astrojs/mdx';
import rehypeSlug from 'rehype-slug';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'astro/config';
import siteConfig from './src/data/site-config';

// https://astro.build/config
export default defineConfig({
    site: siteConfig.website,
    base: '/scc-blog',
    markdown: {
        rehypePlugins: [rehypeSlug]
    },
    vite: {
        plugins: [tailwindcss()]
    },
    integrations: [mdx(), sitemap()]
});
