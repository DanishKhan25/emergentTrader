import { NextResponse } from 'next/server'
import { spawn } from 'child_process'

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
    const result = await callPythonAuth('refresh', { token })
    
    if (result.success) {
      return NextResponse.json(result)
    } else {
      return NextResponse.json(result, { status: 401 })
    }

  } catch (error) {
    console.error('Token refresh error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 })
  }
}

async function callPythonAuth(action, data) {
  return new Promise((resolve, reject) => {
    const pythonScript = `
import sys
import os
sys.path.append('${process.cwd()}/python_backend')
from services.auth_service import auth_service
import json

try:
    if '${action}' == 'refresh':
        result = auth_service.refresh_token('${data.token}')
    else:
        result = {'success': False, 'error': 'Invalid action'}
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
`

    const pythonProcess = spawn('python3', ['-c', pythonScript])
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
        resolve({ success: false, error: 'Token refresh failed' })
      }
    })
  })
}
