import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

import { onRequest } from './src/middleware.js';

export default defineConfig({
  output: "server", 
  integrations: [react()],
  server: {
    middleware: [onRequest],
  },
});
