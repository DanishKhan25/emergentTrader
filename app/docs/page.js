'use client'

import dynamic from 'next/dynamic'
import { useState, useEffect } from 'react'

// Dynamically import SwaggerUI to avoid SSR issues
const SwaggerUI = dynamic(() => import('swagger-ui-react'), { ssr: false })

export default function ApiDocsPage() {
  const [swaggerSpec, setSwaggerSpec] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Fetch the swagger spec from our API
    fetch('/api/docs/swagger.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load API documentation')
        }
        return response.json()
      })
      .then(spec => {
        setSwaggerSpec(spec)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading API Documentation...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-8">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-2">EmergentTrader API Documentation</h1>
          <p className="text-xl opacity-90">AI-Powered Trading Signal Platform API</p>
          <div className="mt-4 flex flex-wrap gap-4">
            <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
              Version 1.0.0
            </span>
            <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
              OpenAPI 3.0
            </span>
            <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
              REST API
            </span>
          </div>
        </div>
      </div>
      
      <div className="container mx-auto px-4 py-8">
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <strong>Getting Started:</strong> This API provides endpoints for stock data, trading signal generation, backtesting, and performance analytics. 
                All endpoints return JSON responses with a consistent structure including success status, data, and error fields.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Base URL</h3>
            <code className="text-sm bg-gray-100 px-2 py-1 rounded">http://localhost:3000/api</code>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Response Format</h3>
            <code className="text-sm bg-gray-100 px-2 py-1 rounded">application/json</code>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Authentication</h3>
            <span className="text-sm text-gray-600">None required (Development)</span>
          </div>
        </div>
      </div>

      {swaggerSpec && (
        <div className="swagger-container">
          <SwaggerUI 
            spec={swaggerSpec}
            docExpansion="list"
            defaultModelsExpandDepth={2}
            defaultModelExpandDepth={2}
            displayRequestDuration={true}
            tryItOutEnabled={true}
            filter={true}
            showExtensions={true}
            showCommonExtensions={true}
          />
        </div>
      )}

      <style jsx global>{`
        .swagger-container {
          padding: 0 2rem 2rem 2rem;
        }
        
        .swagger-ui .topbar {
          display: none;
        }
        
        .swagger-ui .info {
          margin: 20px 0;
        }
        
        .swagger-ui .scheme-container {
          background: #fafafa;
          padding: 10px;
          border-radius: 4px;
          margin: 20px 0;
        }
        
        .swagger-ui .opblock.opblock-get {
          border-color: #61affe;
          background: rgba(97, 175, 254, 0.1);
        }
        
        .swagger-ui .opblock.opblock-post {
          border-color: #49cc90;
          background: rgba(73, 204, 144, 0.1);
        }
        
        .swagger-ui .opblock.opblock-put {
          border-color: #fca130;
          background: rgba(252, 161, 48, 0.1);
        }
        
        .swagger-ui .opblock.opblock-delete {
          border-color: #f93e3e;
          background: rgba(249, 62, 62, 0.1);
        }
        
        .swagger-ui .btn.authorize {
          background-color: #4f46e5;
          border-color: #4f46e5;
        }
        
        .swagger-ui .btn.authorize:hover {
          background-color: #4338ca;
          border-color: #4338ca;
        }
      `}</style>
    </div>
  )
}
