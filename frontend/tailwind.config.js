/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        panel: '#0f1117',
        surface: '#1a1f2e',
        border: '#2a2f3e',
        accent: '#6366f1',
      },
    },
  },
  plugins: [],
}
