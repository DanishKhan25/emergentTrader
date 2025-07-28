// Test script to verify the API call issue
const { spawn } = require('child_process')

const pythonScript = `
import sys
import os
sys.path.append('/Users/danishkhan/Development/Clients/emergentTrader/python_backend')
os.chdir('/Users/danishkhan/Development/Clients/emergentTrader/python_backend')
from api_handler import handle_api_request
import json

try:
    result = handle_api_request('stocks/shariah', 'GET', {})
    if isinstance(result, dict) and 'data' in result and 'stocks' in result['data']:
        print(f"Stocks count: {len(result['data']['stocks'])}")
    else:
        print(f"Result: {result}")
except Exception as e:
    print(f"Error: {str(e)}")
`

const pythonProcess = spawn('/opt/homebrew/bin/python3', ['-c', pythonScript])
let output = ''

pythonProcess.stdout.on('data', (data) => {
  output += data.toString()
})

pythonProcess.on('close', (code) => {
  console.log('Python spawn result:', output.trim())
})
