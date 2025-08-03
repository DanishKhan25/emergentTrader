/** @type {import('next').NextConfig} */
const nextConfig = {
  // Production optimizations
  output: 'standalone',
  
  // Environment configuration
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://emergenttrader-backend.onrender.com',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'wss://emergenttrader-backend.onrender.com',
    NEXT_PUBLIC_APP_NAME: 'EmergentTrader',
    NEXT_PUBLIC_APP_VERSION: '2.0.0',
  },

  // Image optimization
  images: {
    domains: ['emergenttrader.onrender.com'],
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60,
  },

  // Compression
  compress: true,

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ]
  },

  // Redirects for API calls
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://emergenttrader-backend.onrender.com'}/api/:path*`,
      },
      {
        source: '/ws',
        destination: `${process.env.NEXT_PUBLIC_WS_URL || 'wss://emergenttrader-backend.onrender.com'}/ws`,
      },
    ]
  },

  // Webpack configuration
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Production optimizations
    if (!dev) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      }
    }

    return config
  },

  // Experimental features
  experimental: {
    // Enable app directory
    appDir: true,
    
    // Server components
    serverComponentsExternalPackages: ['@prisma/client'],
    
    // Optimize CSS
    optimizeCss: true,
    
    // Optimize fonts
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },

  // Build configuration
  generateBuildId: async () => {
    // Use git commit hash or timestamp
    return process.env.RENDER_GIT_COMMIT || `build-${Date.now()}`
  },

  // Logging
  logging: {
    fetches: {
      fullUrl: true,
    },
  },

  // TypeScript configuration
  typescript: {
    // Ignore build errors in production (handle separately)
    ignoreBuildErrors: process.env.NODE_ENV === 'production',
  },

  // ESLint configuration
  eslint: {
    // Ignore during builds (handle separately)
    ignoreDuringBuilds: process.env.NODE_ENV === 'production',
  },

  // Static file serving
  trailingSlash: false,
  
  // Power by header
  poweredByHeader: false,

  // React strict mode
  reactStrictMode: true,

  // SWC minification
  swcMinify: true,

  // Bundle analyzer (only in development)
  ...(process.env.ANALYZE === 'true' && {
    webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
      const { BundleAnalyzerPlugin } = require('@next/bundle-analyzer')()
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
        })
      )
      return config
    },
  }),
}

module.exports = nextConfig
