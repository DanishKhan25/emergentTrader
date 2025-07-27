/**
 * WebSocket utility for real-time updates
 * Handles connection, reconnection, and message handling
 */

class EmergentTraderWebSocket {
  constructor(url = 'ws://localhost:8000/ws') {
    this.url = url
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.listeners = new Map()
    this.isConnecting = false
    this.shouldReconnect = true
  }

  connect() {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return
    }

    this.isConnecting = true

    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected to EmergentTrader')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.emit('connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason)
        this.isConnecting = false
        this.emit('disconnected')
        
        if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        this.isConnecting = false
        this.emit('error', error)
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      this.isConnecting = false
    }
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  scheduleReconnect() {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
    
    setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect()
      }
    }, delay)
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
      return true
    } else {
      console.warn('WebSocket not connected, message not sent:', message)
      return false
    }
  }

  handleMessage(data) {
    const { type } = data
    
    switch (type) {
      case 'connection':
        console.log('📡 WebSocket connection confirmed:', data.message)
        break
      
      case 'pong':
        this.emit('pong', data)
        break
      
      case 'portfolio_update':
        this.emit('portfolio_update', data.data)
        break
      
      default:
        this.emit('message', data)
    }
  }

  // Event system
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${event}:`, error)
        }
      })
    }
  }

  // Utility methods
  ping() {
    return this.send({ type: 'ping' })
  }

  subscribeToPortfolio() {
    return this.send({ type: 'subscribe_portfolio' })
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }

  getConnectionState() {
    if (!this.ws) return 'disconnected'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'connected'
      case WebSocket.CLOSING: return 'closing'
      case WebSocket.CLOSED: return 'disconnected'
      default: return 'unknown'
    }
  }
}

// Global instance
let wsInstance = null

export const getWebSocket = () => {
  if (!wsInstance) {
    wsInstance = new EmergentTraderWebSocket()
  }
  return wsInstance
}

export const connectWebSocket = () => {
  const ws = getWebSocket()
  ws.connect()
  return ws
}

export const disconnectWebSocket = () => {
  if (wsInstance) {
    wsInstance.disconnect()
    wsInstance = null
  }
}

export default EmergentTraderWebSocket
