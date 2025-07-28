import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request) {
  try {
    const { username, password } = await request.json()

    if (!username || !password) {
      return NextResponse.json({
        success: false,
        error: 'Username and password are required'
      }, { status: 400 })
    }

    // Call Python authentication service
    const result = await callPythonAuth('login', { username, password })
    
    if (result.success) {
      return NextResponse.json(result)
    } else {
      return NextResponse.json(result, { status: 401 })
    }

  } catch (error) {
    console.error('Login API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 })
  }
}

async function callPythonAuth(action, data) {
  return new Promise((resolve, reject) => {
    const backendPath = path.join(process.cwd(), 'python_backend')
    const venvPython = path.join(backendPath, 'venv', 'bin', 'python3')
    
    const pythonScript = `
import sys
import os
sys.path.append('${backendPath}')

try:
    # Try to import JWT-based auth service first
    try:
        from services.auth_service import auth_service
        auth_service_instance = auth_service
    except ImportError:
        # Fallback to simple auth service if JWT not available
        from services.fallback_auth_service import fallback_auth_service
        auth_service_instance = fallback_auth_service
    
    import json

    if '${action}' == 'login':
        result = auth_service_instance.authenticate('${data.username}', '${data.password}')
    elif '${action}' == 'verify':
        result = auth_service_instance.verify_token('${data.token}')
    elif '${action}' == 'refresh':
        result = auth_service_instance.refresh_token('${data.token}')
    elif '${action}' == 'logout':
        result = auth_service_instance.logout('${data.token}')
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
        resolve({ success: false, error: errorOutput || 'Authentication failed' })
      }
    })

    pythonProcess.on('error', (error) => {
      console.error('Python spawn error:', error)
      resolve({ success: false, error: error.message })
    })
  })
}
