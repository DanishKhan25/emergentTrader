import { NextResponse } from 'next/server'
import { spawn } from 'child_process'

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
    const pythonScript = `
import sys
import os
sys.path.append('${process.cwd()}/python_backend')
from services.auth_service import auth_service
import json

try:
    if '${action}' == 'logout':
        result = auth_service.logout('${data.token}')
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
      try {
        const result = JSON.parse(output.trim())
        resolve(result)
      } catch (error) {
        resolve({ success: true, message: 'Logged out successfully' })
      }
    })
  })
}
