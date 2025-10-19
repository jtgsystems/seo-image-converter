// vite.config.mjs
import { sveltekit } from "file:///home/ultron/Desktop/JTG-AI-IMAGE-CONVERTER/jtg-ai-image-converter/node_modules/@sveltejs/kit/src/exports/vite/index.js";
var vite_config_default = {
  plugins: [sveltekit()],
  build: {
    target: "esnext",
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        compact: true,
        manualChunks: {
          // Split Tauri API into separate chunk for better caching
          "tauri": ["@tauri-apps/api/tauri", "@tauri-apps/api/event", "@tauri-apps/api/dialog"],
          // Separate vendor chunk 
          "vendor": ["svelte/store", "svelte"]
        }
      }
    },
    minify: "esbuild"
    // Use esbuild for faster builds, terser for production
  },
  ssr: {
    noExternal: ["@tauri-apps/api"]
  }
};
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcubWpzIl0sCiAgInNvdXJjZXNDb250ZW50IjogWyJjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZGlybmFtZSA9IFwiL2hvbWUvdWx0cm9uL0Rlc2t0b3AvSlRHLUFJLUlNQUdFLUNPTlZFUlRFUi9qdGctYWktaW1hZ2UtY29udmVydGVyXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvaG9tZS91bHRyb24vRGVza3RvcC9KVEctQUktSU1BR0UtQ09OVkVSVEVSL2p0Zy1haS1pbWFnZS1jb252ZXJ0ZXIvdml0ZS5jb25maWcubWpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9ob21lL3VsdHJvbi9EZXNrdG9wL0pURy1BSS1JTUFHRS1DT05WRVJURVIvanRnLWFpLWltYWdlLWNvbnZlcnRlci92aXRlLmNvbmZpZy5tanNcIjtpbXBvcnQgeyBzdmVsdGVraXQgfSBmcm9tICdAc3ZlbHRlanMva2l0L3ZpdGUnO1xuXG5leHBvcnQgZGVmYXVsdCB7XG4gIHBsdWdpbnM6IFtzdmVsdGVraXQoKV0sXG4gIGJ1aWxkOiB7XG4gICAgdGFyZ2V0OiAnZXNuZXh0JyxcbiAgICBjc3NDb2RlU3BsaXQ6IHRydWUsXG4gICAgcm9sbHVwT3B0aW9uczoge1xuICAgICAgb3V0cHV0OiB7XG4gICAgICAgIGNvbXBhY3Q6IHRydWUsXG4gICAgICAgIG1hbnVhbENodW5rczoge1xuICAgICAgICAgIC8vIFNwbGl0IFRhdXJpIEFQSSBpbnRvIHNlcGFyYXRlIGNodW5rIGZvciBiZXR0ZXIgY2FjaGluZ1xuICAgICAgICAgICd0YXVyaSc6IFsnQHRhdXJpLWFwcHMvYXBpL3RhdXJpJywgJ0B0YXVyaS1hcHBzL2FwaS9ldmVudCcsICdAdGF1cmktYXBwcy9hcGkvZGlhbG9nJ10sXG4gICAgICAgICAgLy8gU2VwYXJhdGUgdmVuZG9yIGNodW5rIFxuICAgICAgICAgICd2ZW5kb3InOiBbJ3N2ZWx0ZS9zdG9yZScsICdzdmVsdGUnXVxuICAgICAgICB9XG4gICAgICB9XG4gICAgfSxcbiAgICBtaW5pZnk6ICdlc2J1aWxkJyAvLyBVc2UgZXNidWlsZCBmb3IgZmFzdGVyIGJ1aWxkcywgdGVyc2VyIGZvciBwcm9kdWN0aW9uXG4gIH0sXG4gIHNzcjoge1xuICAgIG5vRXh0ZXJuYWw6IFsnQHRhdXJpLWFwcHMvYXBpJ11cbiAgfVxufTtcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBMFgsU0FBUyxpQkFBaUI7QUFFcFosSUFBTyxzQkFBUTtBQUFBLEVBQ2IsU0FBUyxDQUFDLFVBQVUsQ0FBQztBQUFBLEVBQ3JCLE9BQU87QUFBQSxJQUNMLFFBQVE7QUFBQSxJQUNSLGNBQWM7QUFBQSxJQUNkLGVBQWU7QUFBQSxNQUNiLFFBQVE7QUFBQSxRQUNOLFNBQVM7QUFBQSxRQUNULGNBQWM7QUFBQTtBQUFBLFVBRVosU0FBUyxDQUFDLHlCQUF5Qix5QkFBeUIsd0JBQXdCO0FBQUE7QUFBQSxVQUVwRixVQUFVLENBQUMsZ0JBQWdCLFFBQVE7QUFBQSxRQUNyQztBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsSUFDQSxRQUFRO0FBQUE7QUFBQSxFQUNWO0FBQUEsRUFDQSxLQUFLO0FBQUEsSUFDSCxZQUFZLENBQUMsaUJBQWlCO0FBQUEsRUFDaEM7QUFDRjsiLAogICJuYW1lcyI6IFtdCn0K
