/** @type {import('next').NextConfig} */
const nextConfig = {
  // Compression
  compress: true,

  // Production optimizations
  poweredByHeader: false,

  // Experimental features for better performance
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['lucide-react'],
  },
};

export default nextConfig;
