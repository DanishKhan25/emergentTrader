/**
 * Dynamic API Service for EmergentTrader
 * Handles all real backend API calls with error handling and caching
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiService {
  constructor() {
    this.cache = new Map()
    this.cacheTimeout = 30000 // 30 seconds
  }

  async request(endpoint, options = {}) {
    const {
      method = 'GET',
      body = null,
      headers = {},
      cache = false,
      timeout = 30000
    } = options

    // Check cache first
    if (cache && method === 'GET') {
      const cached = this.getFromCache(endpoint)
      if (cached) return cached
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: body ? JSON.stringify(body) : null,
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      // Cache successful GET requests
      if (cache && method === 'GET') {
        this.setCache(endpoint, data)
      }

      return data
    } catch (error) {
      clearTimeout(timeoutId)
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout')
      }
      
      throw error
    }
  }

  getFromCache(key) {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data
    }
    this.cache.delete(key)
    return null
  }

  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  clearCache() {
    this.cache.clear()
  }

  // Stock Data APIs
  async getStocks(shariahOnly = false) {
    const endpoint = shariahOnly ? '/stocks/shariah' : '/stocks/all'
    return this.request(endpoint, { cache: true })
  }

  async getStock(symbol) {
    return this.request(`/stock/${symbol}`, { cache: true })
  }

  async refreshStockPrices() {
    return this.request('/stocks/refresh', { method: 'POST' })
  }

  // Signal APIs
  async generateSignals(options = {}) {
    const {
      strategy = 'multibagger',
      symbols = null,
      shariah_only = true,
      min_confidence = 0.7
    } = options

    return this.request('/signals/generate', {
      method: 'POST',
      body: {
        strategy,
        symbols,
        shariah_only,
        min_confidence
      }
    })
  }

  async getTodaySignals() {
    return this.request('/signals/today', { cache: true })
  }

  async getOpenSignals() {
    return this.request('/signals/open', { cache: true })
  }

  async getSignalHistory(limit = 50) {
    return this.request(`/signals/history?limit=${limit}`, { cache: true })
  }

  async trackSignals(signalIds) {
    return this.request('/signals/track', {
      method: 'POST',
      body: { signal_ids: signalIds }
    })
  }

  // Strategy APIs
  async getStrategies() {
    return this.request('/strategies', { cache: true })
  }

  async runBacktest(options = {}) {
    const {
      strategy = 'multibagger',
      start_date = '2019-01-01',
      end_date = '2025-01-27',
      symbols = null
    } = options

    return this.request('/backtest', {
      method: 'POST',
      body: {
        strategy,
        start_date,
        end_date,
        symbols
      }
    })
  }

  // Performance APIs
  async getPerformanceSummary(period = '30d') {
    return this.request(`/performance/summary?period=${period}`, { cache: true })
  }

  async getPortfolioData() {
    return this.request('/portfolio', { cache: true })
  }

  async getAnalytics(timeRange = '6m') {
    return this.request(`/analytics?range=${timeRange}`, { cache: true })
  }

  // System APIs
  async getSystemHealth() {
    return this.request('/health')
  }

  async getSystemStatus() {
    return this.request('/status', { cache: true })
  }

  // Notification APIs
  async sendTestNotification(type = 'telegram') {
    return this.request('/notifications/test', {
      method: 'POST',
      body: { type }
    })
  }

  async updateNotificationSettings(settings) {
    return this.request('/notifications/settings', {
      method: 'PUT',
      body: settings
    })
  }

  // Real-time data subscription
  async subscribeToUpdates(callback) {
    if (typeof EventSource === 'undefined') {
      console.warn('EventSource not supported')
      return null
    }

    const eventSource = new EventSource(`${API_BASE_URL}/stream`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        callback(data)
      } catch (error) {
        console.error('Error parsing SSE data:', error)
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error)
    }

    return eventSource
  }

  // WebSocket connection for real-time updates
  connectWebSocket(onMessage, onError = null) {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws'
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('Error parsing WebSocket data:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      // Auto-reconnect after 5 seconds
      setTimeout(() => {
        this.connectWebSocket(onMessage, onError)
      }, 5000)
    }

    return ws
  }
}

// Create singleton instance
const apiService = new ApiService()

export default apiService

// Named exports for convenience
export const {
  getStocks,
  getStock,
  refreshStockPrices,
  generateSignals,
  getTodaySignals,
  getOpenSignals,
  getSignalHistory,
  trackSignals,
  getStrategies,
  runBacktest,
  getPerformanceSummary,
  getPortfolioData,
  getAnalytics,
  getSystemHealth,
  getSystemStatus,
  sendTestNotification,
  updateNotificationSettings,
  subscribeToUpdates,
  connectWebSocket
} = apiService
