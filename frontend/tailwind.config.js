/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'risk-high': '#DC2626',
        'risk-medium': '#EA580C',
        'risk-low': '#16A34A',
        'risk-info': '#2563EB',
      }
    },
  },
  plugins: [],
}
