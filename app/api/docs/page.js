'use client'

export default function ApiDocsPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">EmergentTrader API Documentation</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Base URL</h2>
          <code className="bg-gray-100 px-3 py-1 rounded">
            https://emergenttrader-backend.onrender.com
          </code>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Available Endpoints</h2>
          
          <div className="space-y-4">
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="font-semibold">POST /api/signals/generate</h3>
              <p className="text-gray-600">Generate new trading signals</p>
            </div>
            
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold">GET /api/signals/active</h3>
              <p className="text-gray-600">Get currently active signals</p>
            </div>
            
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="font-semibold">GET /api/health</h3>
              <p className="text-gray-600">Check API health status</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
