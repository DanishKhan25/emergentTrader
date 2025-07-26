import { MongoClient } from 'mongodb'
import { v4 as uuidv4 } from 'uuid'
import { NextResponse } from 'next/server'
import { spawn } from 'child_process'

// MongoDB connection
let client
let db

async function connectToMongo() {
  if (!client) {
    client = new MongoClient(process.env.MONGO_URL)
    await client.connect()
    db = client.db(process.env.DB_NAME)
  }
  return db
}

// Helper function to handle CORS
function handleCORS(response) {
  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  response.headers.set('Access-Control-Allow-Credentials', 'true')
  return response
}

// Helper function to call Python backend
async function callPythonAPI(endpoint, method = 'GET', params = {}) {
  return new Promise((resolve, reject) => {
    const pythonScript = `
import sys
import os
sys.path.append('/app/python_backend')
os.chdir('/app/python_backend')
from api_handler import handle_api_request
import json

try:
    result = handle_api_request('${endpoint}', '${method}', ${JSON.stringify(params)})
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
`
    
    const pythonProcess = spawn('/root/.venv/bin/python3', ['-c', pythonScript], { cwd: '/app/python_backend' })
    let output = ''
    let error = ''
    
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString()
    })
    
    pythonProcess.stderr.on('data', (data) => {
      error += data.toString()
    })
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${error}`))
      } else {
        try {
          // Extract JSON from output (may contain other logs)
          const lines = output.split('\n')
          const jsonLine = lines.find(line => line.trim().startsWith('{'))
          const result = jsonLine ? JSON.parse(jsonLine) : { success: false, error: 'No valid JSON output' }
          resolve(result)
        } catch (e) {
          reject(new Error(`Failed to parse Python output: ${e.message}`))
        }
      }
    })
  })
}

// OPTIONS handler for CORS
export async function OPTIONS() {
  return handleCORS(new NextResponse(null, { status: 200 }))
}

// Route handler function
async function handleRoute(request, { params }) {
  const { path = [] } = params
  const route = `/${path.join('/')}`
  const method = request.method

  try {
    const db = await connectToMongo()

    // Root endpoint - GET /api/root
    if (route === '/root' && method === 'GET') {
      return handleCORS(NextResponse.json({ 
        message: "EmergentTrader API v1.0", 
        status: "active",
        timestamp: new Date().toISOString()
      }))
    }

    // Root endpoint - GET /api/
    if (route === '/' && method === 'GET') {
      return handleCORS(NextResponse.json({ 
        message: "EmergentTrader API v1.0 - Your AI-Powered Trading Signal Platform", 
        status: "active",
        timestamp: new Date().toISOString()
      }))
    }

    // Trading Signals Endpoints
    
    // GET /api/signals/today
    if (route === '/signals/today' && method === 'GET') {
      try {
        const result = await callPythonAPI('signals/today', 'GET')
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error getting today signals:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // GET /api/signals/open or /api/signals/active
    if ((route === '/signals/open' || route === '/signals/active') && method === 'GET') {
      try {
        const url = new URL(request.url)
        const strategy = url.searchParams.get('strategy')
        const result = await callPythonAPI('signals/open', 'GET', { strategy })
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error getting open signals:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // POST /api/signals/generate
    if (route === '/signals/generate' && method === 'POST') {
      try {
        const body = await request.json()
        const { strategy = 'momentum', symbols } = body
        
        const result = await callPythonAPI('signals/generate', 'POST', { strategy, symbols })
        
        // Store signals in MongoDB
        if (result.success && result.data.signals) {
          const signalsCollection = db.collection('trading_signals')
          const signalsToStore = result.data.signals.map(signal => ({
            ...signal,
            stored_at: new Date().toISOString(),
            id: uuidv4()
          }))
          
          await signalsCollection.insertMany(signalsToStore)
        }
        
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error generating signals:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // POST /api/signals/track
    if (route === '/signals/track' && method === 'POST') {
      try {
        const body = await request.json()
        const { signal_id } = body
        
        if (!signal_id) {
          return handleCORS(NextResponse.json({
            success: false,
            error: 'signal_id is required'
          }, { status: 400 }))
        }
        
        const result = await callPythonAPI('signals/track', 'POST', { signal_id })
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error tracking signal:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // Backtest Endpoints
    
    // POST /api/backtest
    if (route === '/backtest' && method === 'POST') {
      try {
        const body = await request.json()
        const { 
          strategy = 'momentum', 
          start_date = '2012-01-01', 
          end_date = '2018-12-31',
          symbols 
        } = body
        
        const result = await callPythonAPI('backtest', 'POST', { 
          strategy, start_date, end_date, symbols 
        })
        
        // Store backtest results in MongoDB
        if (result.success) {
          const backtestCollection = db.collection('backtest_results')
          await backtestCollection.insertOne({
            ...result.data,
            id: uuidv4(),
            created_at: new Date().toISOString(),
            requested_by: 'api'
          })
        }
        
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error running backtest:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // GET /api/backtest/results
    if (route === '/backtest/results' && method === 'GET') {
      try {
        const url = new URL(request.url)
        const type = url.searchParams.get('type') || 'backtest'
        
        const result = await callPythonAPI('backtest/results', 'GET', { type })
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error getting backtest results:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // Stock Data Endpoints
    
    // GET /api/stocks/all
    if (route === '/stocks/all' && method === 'GET') {
      try {
        const result = await callPythonAPI('stocks/all', 'GET')
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error getting all stocks:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // GET /api/stocks/shariah
    if (route === '/stocks/shariah' && method === 'GET') {
      try {
        const result = await callPythonAPI('stocks/shariah', 'GET')
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error getting shariah stocks:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // Performance Endpoints
    
    // GET /api/performance/summary
    if (route === '/performance/summary' && method === 'GET') {
      try {
        const url = new URL(request.url)
        const strategy = url.searchParams.get('strategy') || 'momentum'
        
        const result = await callPythonAPI('performance/summary', 'GET', { strategy })
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error getting performance summary:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // POST /api/report/send
    if (route === '/report/send' && method === 'POST') {
      try {
        const body = await request.json()
        const { type = 'daily', recipients } = body
        
        const result = await callPythonAPI('report/send', 'POST', { type, recipients })
        return handleCORS(NextResponse.json(result))
      } catch (error) {
        console.error('Error sending report:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // Database CRUD operations (for dashboard data persistence)
    
    // GET /api/dashboard/stats
    if (route === '/dashboard/stats' && method === 'GET') {
      try {
        const signalsCount = await db.collection('trading_signals').countDocuments()
        const backtestCount = await db.collection('backtest_results').countDocuments()
        
        return handleCORS(NextResponse.json({
          success: true,
          data: {
            total_signals: signalsCount,
            total_backtests: backtestCount,
            last_updated: new Date().toISOString()
          }
        }))
      } catch (error) {
        console.error('Error getting dashboard stats:', error)
        return handleCORS(NextResponse.json({
          success: false,
          error: error.message
        }, { status: 500 }))
      }
    }

    // Route not found
    return handleCORS(NextResponse.json(
      { 
        success: false,
        error: `Route ${route} not found`, 
        available_endpoints: [
          '/signals/today',
          '/signals/open', 
          '/signals/generate',
          '/signals/track',
          '/backtest',
          '/backtest/results',
          '/stocks/all',
          '/stocks/shariah',
          '/performance/summary',
          '/report/send'
        ]
      }, 
      { status: 404 }
    ))

  } catch (error) {
    console.error('API Error:', error)
    return handleCORS(NextResponse.json(
      { 
        success: false,
        error: "Internal server error",
        details: error.message 
      }, 
      { status: 500 }
    ))
  }
}

// Export all HTTP methods
export const GET = handleRoute
export const POST = handleRoute
export const PUT = handleRoute
export const DELETE = handleRoute
export const PATCH = handleRoute