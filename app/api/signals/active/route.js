import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function GET(request) {
  try {
    const result = await callSignalManager('get_active_signals')
    
    if (result.success) {
      return NextResponse.json(result)
    } else {
      return NextResponse.json(result, { status: 500 })
    }

  } catch (error) {
    console.error('Active signals API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 })
  }
}

async function callSignalManager(action, data = {}) {
  return new Promise((resolve, reject) => {
    const backendPath = path.join(process.cwd(), 'python_backend')
    const venvPython = path.join(backendPath, 'venv', 'bin', 'python3')
    
    const pythonScript = `
import sys
import os
sys.path.append('${backendPath}')

try:
    from services.signal_management_service import signal_manager
    import json

    if '${action}' == 'get_active_signals':
        result = signal_manager.get_active_signals()
    elif '${action}' == 'get_statistics':
        result = signal_manager.get_signal_statistics()
    elif '${action}' == 'clear_signals':
        result = signal_manager.clear_all_signals()
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
        resolve({ success: false, error: 'Signal manager call failed' })
      }
    })
  })
}
