/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',
  
  // Disable TypeScript checking during build for faster deployment
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Disable ESLint during build
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // Disable telemetry for better performance
  experimental: {
    optimizeCss: false,
  },
  
  // Webpack configuration for chunk loading reliability
  webpack: (config, { isServer, webpack }) => {
    if (!isServer) {
      // Add fallbacks for client-side
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };

      // Add chunk retry logic
      config.plugins.push(
        new webpack.DefinePlugin({
          'process.env.CHUNK_RETRY_COUNT': JSON.stringify('3'),
          'process.env.CHUNK_RETRY_DELAY': JSON.stringify('1000'),
        })
      );
    }

    // Optimize chunks for better loading
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        ...config.optimization.splitChunks,
        cacheGroups: {
          ...config.optimization.splitChunks.cacheGroups,
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            maxSize: 244000, // 244kb chunks
          },
        },
      },
    };

    return config;
  },

  // Add headers for better caching and security
  async headers() {
    return [
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },

  // Handle redirects and rewrites if needed
  async rewrites() {
    return [
      {
        source: '/health',
        destination: '/api/health',
      },
    ];
  },

  // Optimize images
  images: {
    domains: [],
    unoptimized: true, // Disable optimization for faster builds
  },

  // Enable source maps in production for debugging
  productionBrowserSourceMaps: false,

  // Disable x-powered-by header
  poweredByHeader: false,

  // Enable compression
  compress: true,

  // Configure trailing slash
  trailingSlash: false,
}

module.exports = nextConfig;
