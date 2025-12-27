/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    fontFamily: {
      'sans': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      'heading': ['Poppins', 'Inter', 'sans-serif'],
    },
    extend: {
      colors: {
        'primary': '#5368DF',
        'secondary': '#FA5757',
        'accent': '#34C759',
        'grayish-blue': '#9194A1',
        'dark-blue': '#252B46',
        'light-gray': '#F7F7F7',
      },
      boxShadow: {
        'soft': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'medium': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'strong': '0 8px 24px rgba(0, 0, 0, 0.15)',
      },
    },
  },
  plugins: [],
}

