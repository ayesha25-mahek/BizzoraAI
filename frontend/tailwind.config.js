/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        background: {
          DEFAULT: '#0A0A0F',
          secondary: '#111116',
        },
        surface: {
          DEFAULT: '#1A1A24',
          secondary: '#1E1E2E',
          tertiary: '#252535',
        },
        border: {
          DEFAULT: '#2A2A3A',
          subtle: '#1E1E2E',
          active: '#7C3AED',
        },
        primary: {
          DEFAULT: '#7C3AED',
          hover: '#6D28D9',
          light: '#8B5CF6',
          dark: '#4F46E5',
        },
        accent: {
          violet: '#7C3AED',
          indigo: '#4F46E5',
          purple: '#9333EA',
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)',
        'gradient-surface': 'linear-gradient(135deg, #1A1A24 0%, #1E1E2E 100%)',
        'gradient-glow': 'radial-gradient(ellipse at center, rgba(124, 58, 237, 0.15) 0%, transparent 70%)',
      },
      boxShadow: {
        'glow-sm': '0 0 15px rgba(124, 58, 237, 0.15)',
        'glow-md': '0 0 30px rgba(124, 58, 237, 0.2)',
        'glow-lg': '0 0 60px rgba(124, 58, 237, 0.25)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.4)',
        'card-hover': '0 8px 40px rgba(0, 0, 0, 0.5)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
        'shimmer': 'shimmer 2s linear infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        glow: {
          'from': { boxShadow: '0 0 10px rgba(124, 58, 237, 0.2)' },
          'to': { boxShadow: '0 0 30px rgba(124, 58, 237, 0.5)' },
        },
        slideUp: {
          'from': { opacity: '0', transform: 'translateY(16px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
