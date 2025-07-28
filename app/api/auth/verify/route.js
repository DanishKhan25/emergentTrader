import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request) {
  try {
    const authHeader = request.headers.get('authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({
        success: false,
        error: 'No token provided'
      }, { status: 401 })
    }

    const token = authHeader.substring(7)
    const result = await callPythonAuth('verify', { token })
    
    if (result.success) {
      return NextResponse.json(result)
    } else {
      return NextResponse.json(result, { status: 401 })
    }

  } catch (error) {
    console.error('Token verification error:', error)
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

    if '${action}' == 'verify':
        result = auth_service_instance.verify_token('${data.token}')
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

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString()
    })

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output.trim())
          resolve(result)
        } catch (error) {
          resolve({ success: false, error: 'Failed to parse response' })
        }
      } else {
        resolve({ success: false, error: 'Token verification failed' })
      }
    })
  })
}
