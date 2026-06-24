/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './home/templates/**/*.html',
    './accounts/templates/**/*.html',
    './backup/templates/**/*.html',
    './bureau_communautaire/templates/**/*.html',
    './commissions/templates/**/*.html',
    './communes_membres/templates/**/*.html',
    './competences/templates/**/*.html',
    './comptes_rendus/templates/**/*.html',
    './conseil_communautaire/templates/**/*.html',
    './contact/templates/**/*.html',
    './journal/templates/**/*.html',
    './linktree/templates/**/*.html',
    './partenaires/templates/**/*.html',
    './rapports_activite/templates/**/*.html',
    './semestriels/templates/**/*.html',
    './services/templates/**/*.html',
  ],
  safelist: [
    'bg-green-700', 'bg-green-800', 'hover:bg-green-800', 'focus-visible:ring-offset-green-800',
    'bg-yellow-700', 'bg-yellow-800', 'hover:bg-yellow-800', 'focus-visible:ring-offset-yellow-800',
    'bg-primary', 'hover:bg-primary-dark', 'focus-visible:ring-offset-primary',
    'bg-green-900/30', 'dark:text-green-200', 'dark:text-green-300',
    'dark:text-blue-300', 'dark:text-blue-400',
    'dark:text-amber-300', 'text-amber-700',
    'text-amber-800', 'dark:text-amber-400',
    'text-green-800', 'text-green-900',
    'focus-visible:outline-none', 'focus-visible:ring-2', 'focus-visible:ring-white',
    'min-h-[44px]', 'min-w-[44px]',
  ],
  theme: {
    extend: {
      colors: {
        // Couleurs optimisées pour l'accessibilité (contraste WCAG AA)
        primary: '#005a9e',        // Bleu plus foncé (contraste ~6:1 avec blanc)
        'primary-dark': '#003f6f', // Bleu très foncé pour contraste renforcé (>7:1)
        secondary: '#7a9f0a',      // Vert plus foncé
        facebook: '#1877F2',
        linkedin: '#0A66C2',
        youtube: '#FF0000',
        instagram: '#E4405F',
        // Couleurs gris étendues avec meilleur contraste
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',  // Plus foncé que le 500 standard
          600: '#4b5563',  // Plus foncé que le 600 standard
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        }
      },
      fontFamily: {
        sans: ['Roboto', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Arial', 'sans-serif'],
      },
    },
  },
  darkMode: 'class',
  plugins: [],
}
