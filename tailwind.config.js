/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {
      sm: '480px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
    },
    extend: {
      colors: {
        ink: {
          950: '#14171F',
          700: '#3A4050',
          500: '#6B7280',
        },
        paper: {
          0: '#FDFCFA',
          100: '#F3F1EC',
          200: '#EAE7DF',
        },
        line: {
          200: '#E4E1D8',
          300: '#D5D1C5',
        },
        evidence: {
          100: '#E7EEEA',
          600: '#2F5D50',
          700: '#254a40',
        },
        'signal-amber': {
          100: '#F5E9D8',
          600: '#A6620C',
        },
        error: {
          100: '#F5E2DE',
          700: '#9A2E1F',
        },
      },
      fontFamily: {
        serif: ['"Source Serif 4"', 'Georgia', 'serif'],
        sans: ['"Inter"', '-apple-system', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      fontSize: {
        xs: ['12px', { lineHeight: '1.4' }],
        sm: ['14px', { lineHeight: '1.45' }],
        base: ['15px', { lineHeight: '1.55' }],
        md: ['17px', { lineHeight: '1.75' }],
        lg: ['20px', { lineHeight: '1.4' }],
        xl: ['26px', { lineHeight: '1.3' }],
        '2xl': ['32px', { lineHeight: '1.25' }],
      },
      lineHeight: {
        tight: '1.3',
        normal: '1.55',
        relaxed: '1.75',
      },
      borderRadius: {
        sm: '3px',
        md: '6px',
        pill: '999px',
      },
      spacing: {
        'sidebar-w': '240px',
        'sidebar-rail': '56px',
        'artifact-w': '440px',
        'header-h': '56px',
        'measure': '680px',
      },
      transitionDuration: {
        fast: '120ms',
        base: '220ms',
      },
      transitionTimingFunction: {
        'ease-out': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}
