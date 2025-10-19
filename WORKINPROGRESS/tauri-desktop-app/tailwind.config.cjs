/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      // Only include needed utilities
      spacing: {
        '72': '18rem',
        '80': '20rem',
        '96': '24rem',
      }
    },
  },
  plugins: [],
  corePlugins: {
    // Disable unused plugins for smaller bundle
    container: false,
    accessibility: false,
    appearance: false,
  },
};
