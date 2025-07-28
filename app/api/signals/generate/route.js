import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request) {
  try {
    const { strategy = 'multibagger', min_confidence = 0.7, shariah_only = true } = await request.json()

    const result = await callSignalGenerator('generate_signals', {
      strategy,
      min_confidence,
      shariah_only
    })
    
    if (result.success) {
      return NextResponse.json(result)
    } else {
      return NextResponse.json(result, { status: 500 })
    }

  } catch (error) {
    console.error('Generate signals API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 })
  }
}

async function callSignalGenerator(action, data = {}) {
  return new Promise((resolve, reject) => {
    const backendPath = path.join(process.cwd(), 'python_backend')
    const venvPython = path.join(backendPath, 'venv', 'bin', 'python3')
    
    const pythonScript = `
import sys
import os
sys.path.append('${backendPath}')

try:
    # Try to use enhanced signal generator if available
    try:
        from core.signal_generator_with_notifications import signal_generator_with_notifications
        signal_generator = signal_generator_with_notifications
        use_enhanced = True
    except ImportError:
        from api_handler import EmergentTraderAPI
        signal_generator = EmergentTraderAPI()
        use_enhanced = False
    
    import json
    import asyncio

    async def generate_signals():
        if '${action}' == 'generate_signals':
            if use_enhanced:
                result = await signal_generator.generate_and_notify_signals(
                    strategy='${data.strategy}',
                    shariah_only=${str(data.shariah_only).lower()},
                    min_confidence=${data.min_confidence},
                    force_refresh=True
                )
            else:
                result = signal_generator.generate_signals(force_refresh=True)
        else:
            result = {'success': False, 'error': 'Invalid action'}
        
        return result

    # Run the async function
    result = asyncio.run(generate_signals())
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
        resolve({ success: false, error: errorOutput || 'Signal generation failed' })
      }
    })

    pythonProcess.on('error', (error) => {
      console.error('Python spawn error:', error)
      resolve({ success: false, error: error.message })
    })
  })
}
