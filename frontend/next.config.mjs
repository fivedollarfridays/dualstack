/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standalone output for Docker deployments
  output: 'standalone',

  // Compression
  compress: true,

  // Production optimizations
  poweredByHeader: false,

  // Experimental features for better performance
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['lucide-react'],
  },

  // Security headers
  async headers() {
    const csp = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.clerk.accounts.dev",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https://*.clerk.accounts.dev https://img.clerk.com",
      "font-src 'self'",
      "connect-src 'self' https://*.clerk.accounts.dev https://api.stripe.com",
      "frame-src https://js.stripe.com https://*.clerk.accounts.dev",
      "worker-src 'self' blob:",
    ].join('; ');

    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains',
          },
          { key: 'Content-Security-Policy', value: csp },
        ],
      },
    ];
  },
};

export default nextConfig;
