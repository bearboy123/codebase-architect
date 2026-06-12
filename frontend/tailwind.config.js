module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'health-excellent': '#10b981',
        'health-good': '#3b82f6',
        'health-fair': '#f59e0b',
        'health-poor': '#ef4444',
      },
      animation: {
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin': 'spin 1s linear infinite',
      }
    },
  },
  plugins: [],
}
