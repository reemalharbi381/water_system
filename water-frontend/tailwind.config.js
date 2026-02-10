/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'qatra-blue': '#0054A6',
        'qatra-light': '#00A3E0',
      },
    },
  },
  plugins: [],
}