import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#070B14',
        'bg-secondary': '#111827',
        accent: '#4F9EFF',
        glow: '#7AE7FF',
      },
      fontFamily: {
        inter: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        space: ['var(--font-space)', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

export default config
