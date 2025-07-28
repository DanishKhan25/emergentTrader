import { NextResponse } from 'next/server'
import { spawn } from 'child_process'

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
    const pythonScript = `
import sys
import os
sys.path.append('${process.cwd()}/python_backend')
from services.auth_service import auth_service
import json

try:
    if '${action}' == 'login':
        result = auth_service.authenticate('${data.username}', '${data.password}')
    elif '${action}' == 'verify':
        result = auth_service.verify_token('${data.token}')
    elif '${action}' == 'refresh':
        result = auth_service.refresh_token('${data.token}')
    elif '${action}' == 'logout':
        result = auth_service.logout('${data.token}')
    else:
        result = {'success': False, 'error': 'Invalid action'}
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
`

    const pythonProcess = spawn('python3', ['-c', pythonScript])
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
          resolve({ success: false, error: 'Failed to parse response' })
        }
      } else {
        resolve({ success: false, error: errorOutput || 'Authentication failed' })
      }
    })

    pythonProcess.on('error', (error) => {
      resolve({ success: false, error: error.message })
    })
  })
}
