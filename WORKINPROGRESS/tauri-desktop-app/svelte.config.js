import adapter from "@sveltejs/adapter-static";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html', // SPA mode for Tauri compatibility
      precompress: false,
      strict: false
    }),
    serviceWorker: {
      register: false // Disable service worker in Tauri context
    }
  },
};

export default config;
