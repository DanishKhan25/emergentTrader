import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://emergenttrader-backend.onrender.com'

export async function GET(request, { params }) {
  return proxyRequest(request, params, 'GET')
}

export async function POST(request, { params }) {
  return proxyRequest(request, params, 'POST')
}

export async function PUT(request, { params }) {
  return proxyRequest(request, params, 'PUT')
}

export async function DELETE(request, { params }) {
  return proxyRequest(request, params, 'DELETE')
}

async function proxyRequest(request, params, method) {
  try {
    const path = params.path ? params.path.join('/') : ''
    const url = new URL(request.url)
    const searchParams = url.searchParams.toString()
    const backendUrl = `${BACKEND_URL}/api/${path}${searchParams ? `?${searchParams}` : ''}`

    const headers = {
      'Content-Type': 'application/json',
    }

    // Copy relevant headers from original request
    const authHeader = request.headers.get('authorization')
    if (authHeader) {
      headers.authorization = authHeader
    }

    let body = undefined
    if (method !== 'GET' && method !== 'DELETE') {
      try {
        body = await request.text()
      } catch (error) {
        // If body parsing fails, continue without body
      }
    }

    const response = await fetch(backendUrl, {
      method,
      headers,
      body,
    })

    const data = await response.text()
    
    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('content-type') || 'application/json',
      },
    })

  } catch (error) {
    console.error('API proxy error:', error)
    return NextResponse.json(
      { error: 'Internal server error', message: error.message },
      { status: 500 }
    )
  }
}
