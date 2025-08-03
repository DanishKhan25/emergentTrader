/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://emergenttrader-backend.onrender.com',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'wss://emergenttrader-backend.onrender.com',
    NEXT_PUBLIC_APP_NAME: 'EmergentTrader',
    NEXT_PUBLIC_APP_VERSION: '2.0.0',
  },

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://emergenttrader-backend.onrender.com'}/api/:path*`,
      },
    ]
  },

  reactStrictMode: true,
  swcMinify: true,
  poweredByHeader: false,
  
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig
