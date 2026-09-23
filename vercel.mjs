// Set SAMJHA_API_ORIGIN to the HTTPS origin of the persistent API service.
// Fail closed: a UI-only deployment would leave login and chat broken.
const raw = process.env.SAMJHA_API_ORIGIN;
if (!raw) throw new Error('SAMJHA_API_ORIGIN is required for a working Samjha deployment.');
const api = new URL(raw);
if (api.protocol !== 'https:' || api.username || api.password || api.pathname !== '/' || api.search || api.hash) {
  throw new Error('SAMJHA_API_ORIGIN must be a bare HTTPS origin.');
}

export const config = {
  framework: 'vite',
  buildCommand: 'VITE_SAMJHA_HOSTED=true npm run build',
  outputDirectory: 'dist',
  rewrites: [
    { source: '/api/:path*', destination: `${api.origin}/api/:path*` },
    { source: '/(.*)', destination: '/index.html' },
  ],
  headers: [
    { source: '/api/:path*', headers: [{ key: 'Cache-Control', value: 'no-store' }] },
  ],
};
