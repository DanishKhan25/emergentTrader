import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request) {
  try {
    const authHeader = request.headers.get('authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({
        success: true,
        message: 'Logged out successfully'
      })
    }

    const token = authHeader.substring(7)
    const result = await callPythonAuth('logout', { token })
    
    return NextResponse.json(result)

  } catch (error) {
    console.error('Logout error:', error)
    return NextResponse.json({
      success: true,
      message: 'Logged out successfully'
    })
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
    from services.auth_service import auth_service
    import json

    if '${action}' == 'logout':
        result = auth_service.logout('${data.token}')
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
      try {
        const result = JSON.parse(output.trim())
        resolve(result)
      } catch (error) {
        resolve({ success: true, message: 'Logged out successfully' })
      }
    })
  })
}
