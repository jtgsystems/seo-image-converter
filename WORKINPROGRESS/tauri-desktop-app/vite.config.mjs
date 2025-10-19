import { sveltekit } from '@sveltejs/kit/vite';

export default {
  plugins: [sveltekit()],
  build: {
    target: 'esnext',
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        compact: true,
        manualChunks: {
          // Split Tauri API into separate chunk for better caching
          'tauri': ['@tauri-apps/api/tauri', '@tauri-apps/api/event', '@tauri-apps/api/dialog'],
          // Separate vendor chunk 
          'vendor': ['svelte/store', 'svelte']
        }
      }
    },
    minify: 'esbuild' // Use esbuild for faster builds, terser for production
  },
  ssr: {
    noExternal: ['@tauri-apps/api']
  }
};
