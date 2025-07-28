import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function GET(request) {
  try {
    // Get signals from the existing API handler
    const result = await callPythonAPI('get_signals')
    
    if (result.success) {
      return NextResponse.json(result)
    } else {
      return NextResponse.json(result, { status: 500 })
    }

  } catch (error) {
    console.error('Signals API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 })
  }
}

async function callPythonAPI(action, data = {}) {
  return new Promise((resolve, reject) => {
    const backendPath = path.join(process.cwd(), 'python_backend')
    const venvPython = path.join(backendPath, 'venv', 'bin', 'python3')
    
    const pythonScript = `
import sys
import os
sys.path.append('${backendPath}')

try:
    from api_handler import EmergentTraderAPI
    import json

    api = EmergentTraderAPI()
    
    if '${action}' == 'get_signals':
        # Get signals from the API handler
        result = api.generate_signals(force_refresh=False)
    else:
        result = {'success': False, 'error': 'Invalid action'}
    
    print(json.dumps(result))
except Exception as e:
    import traceback
    print(json.dumps({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}))
`

    // Try virtual environment python first, fallback to system python
    let pythonCmd = venvPython
    if (!require('fs').existsSync(venvPython)) {
      pythonCmd = 'python3'
    }

    const pythonProcess = spawn(pythonCmd, ['-c', pythonScript], {
      cwd: backendPath
    })
    
    let output = ''
    let errorOutput = ''

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString()
    })

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString()
    })

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output.trim())
          resolve(result)
        } catch (error) {
          console.error('Failed to parse Python output:', output)
          resolve({ success: false, error: 'Failed to parse response' })
        }
      } else {
        console.error('Python process error:', errorOutput)
        resolve({ success: false, error: errorOutput || 'API call failed' })
      }
    })

    pythonProcess.on('error', (error) => {
      console.error('Python spawn error:', error)
      resolve({ success: false, error: error.message })
    })
  })
}
