/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}", // Ito ang pinaka-importanteng linya
  ],
  theme: {
    extend: {
      // Pwede tayong magdagdag ng custom colors dito para mas madali
      colors: {
        'neural-dark': '#050814',
        'neural-deep': '#0D1425',
        'swarm-cyan': '#00F0FF',
        'debate-purple': '#A855F7',
      }
    },
  },
  plugins: [],
};


