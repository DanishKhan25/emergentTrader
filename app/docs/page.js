'use client'

import { useState } from 'react'

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState('overview')

  const sections = {
    overview: {
      title: 'API Overview',
      content: (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">EmergentTrader API</h2>
          <p className="text-gray-600">
            The EmergentTrader API provides automated trading signal generation with Telegram notifications.
          </p>
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Features:</h3>
            <ul className="list-disc list-inside space-y-1">
              <li>3 automated daily scans (9 AM, 2 PM, 6 PM IST)</li>
              <li>Multiple trading strategies</li>
              <li>ML-enhanced signal confidence</li>
              <li>Telegram notifications</li>
              <li>Real-time WebSocket updates</li>
            </ul>
          </div>
        </div>
      )
    },
    endpoints: {
      title: 'API Endpoints',
      content: (
        <div className="space-y-6">
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold text-green-600">POST /api/signals/generate</h3>
            <p className="text-gray-600 mb-2">Generate trading signals</p>
            <div className="bg-gray-100 p-3 rounded text-sm">
              <pre>{`{
  "strategy": "multibagger",
  "min_confidence": 0.7,
  "limit": 20
}`}</pre>
            </div>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-600">GET /api/signals/active</h3>
            <p className="text-gray-600 mb-2">Get active trading signals</p>
            <div className="bg-gray-100 p-3 rounded text-sm">
              <pre>GET /api/signals/active?days=7</pre>
            </div>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold text-purple-600">GET /api/health</h3>
            <p className="text-gray-600 mb-2">Check API health status</p>
            <div className="bg-gray-100 p-3 rounded text-sm">
              <pre>{`{
  "status": "healthy",
  "database": "connected",
  "telegram": "configured",
  "version": "2.0.0"
}`}</pre>
            </div>
          </div>
        </div>
      )
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 bg-white rounded-lg shadow p-6">
            <h1 className="text-xl font-bold mb-6">Documentation</h1>
            <nav className="space-y-2">
              {Object.entries(sections).map(([key, section]) => (
                <button
                  key={key}
                  onClick={() => setActiveSection(key)}
                  className={`w-full text-left px-3 py-2 rounded transition-colors ${
                    activeSection === key
                      ? 'bg-blue-100 text-blue-700'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {section.title}
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 bg-white rounded-lg shadow p-8">
            {sections[activeSection].content}
          </div>
        </div>
      </div>
    </div>
  )
}
