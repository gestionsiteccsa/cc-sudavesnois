/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './home/templates/**/*.html',
    './comptes_rendus/templates/**/*.html',
    './bureau_communautaire/templates/**/*.html',
    './competences/templates/**/*.html',
    './commission/templates/**/*.html',
    './communes_membres/templates/**/*.html',
    './documents/templates/**/*.html',
    './evenements/templates/**/*.html',
    './gestionnaires/templates/**/*.html',
    './membres/templates/**/*.html',
    './notices/templates/**/*.html',
    './publications/templates/**/*.html',
    './services/templates/**/*.html',
    './structures/templates/**/*.html',
    './users/templates/**/*.html',
    './villes/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#006ab3',
        secondary: '#96bf0d',
        facebook: '#1877F2',
        linkedin: '#0A66C2',
        youtube: '#FF0000',
        instagram: '#E4405F'
      },
      fontFamily: {
        sans: ['Roboto', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Arial', 'sans-serif'],
      },
    },
  },
  darkMode: 'class',
  plugins: [],
}