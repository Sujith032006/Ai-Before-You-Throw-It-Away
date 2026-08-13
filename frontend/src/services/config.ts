export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== 'undefined' && window.location.hostname.includes('netlify.app')
    ? 'https://ai-before-you-throw-it-away.onrender.com'
    : 'http://localhost:8000');
