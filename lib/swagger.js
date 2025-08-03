// Simple swagger specification without external dependencies

export const swaggerSpec = {
  openapi: '3.0.0',
  info: {
    title: 'EmergentTrader API',
    version: '2.0.0',
    description: 'Trading signal system with automated signal generation and Telegram notifications',
  },
  servers: [
    {
      url: process.env.NEXT_PUBLIC_API_URL || 'https://emergenttrader-backend.onrender.com',
      description: 'Production server',
    },
  ],
  paths: {
    '/api/signals/generate': {
      post: {
        summary: 'Generate trading signals',
        description: 'Generate trading signals using various strategies',
        responses: {
          200: {
            description: 'Signals generated successfully'
          }
        }
      }
    },
    '/api/signals/active': {
      get: {
        summary: 'Get active signals',
        description: 'Retrieve currently active trading signals',
        responses: {
          200: {
            description: 'Active signals retrieved successfully'
          }
        }
      }
    },
    '/api/health': {
      get: {
        summary: 'Health check',
        description: 'Check the health status of the API',
        responses: {
          200: {
            description: 'Service is healthy'
          }
        }
      }
    }
  }
}

export default swaggerSpec
