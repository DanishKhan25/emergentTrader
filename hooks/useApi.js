'use client'

import { useState, useEffect, useCallback } from 'react'

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30 seconds

// Custom hook for API calls
export function useApi() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const apiCall = useCallback(async (endpoint, options = {}) => {
    const {
      method = 'GET',
      body = null,
      headers = {},
      timeout = API_TIMEOUT,
      retries = 3
    } = options

    setLoading(true)
    setError(null)

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    const requestOptions = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      signal: controller.signal
    }

    if (body && method !== 'GET') {
      requestOptions.body = typeof body === 'string' ? body : JSON.stringify(body)
    }

    let lastError = null

    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions)
        
        clearTimeout(timeoutId)

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()
        setLoading(false)
        return data

      } catch (err) {
        lastError = err
        
        if (err.name === 'AbortError') {
          lastError = new Error('Request timeout')
          break
        }

        // Don't retry on client errors (4xx)
        if (err.message.includes('HTTP 4')) {
          break
        }

        // Wait before retry (exponential backoff)
        if (attempt < retries - 1) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000))
        }
      }
    }

    setError(lastError.message)
    setLoading(false)
    throw lastError
  }, [])

  return { apiCall, loading, error, setError }
}

// Specific hooks for different data types
export function useStocks() {
  const { apiCall, loading, error } = useApi()
  const [stocks, setStocks] = useState([])
  const [shariahStocks, setShariahStocks] = useState([])

  const fetchStocks = useCallback(async (shariahOnly = false) => {
    try {
      const endpoint = shariahOnly ? '/stocks/shariah' : '/stocks/all'
      const data = await apiCall(endpoint)
      
      if (data.success) {
        const stockData = data.stocks || data.data?.stocks || []
        if (shariahOnly) {
          setShariahStocks(stockData)
        } else {
          setStocks(stockData)
        }
        return stockData
      } else {
        throw new Error(data.error || 'Failed to fetch stocks')
      }
    } catch (err) {
      console.error('Error fetching stocks:', err)
      throw err
    }
  }, [apiCall])

  const refreshStockPrices = useCallback(async () => {
    try {
      const data = await apiCall('/stocks/refresh', { method: 'POST' })
      if (data.success) {
        // Refresh both stock lists
        await Promise.all([
          fetchStocks(false),
          fetchStocks(true)
        ])
      }
      return data
    } catch (err) {
      console.error('Error refreshing stock prices:', err)
      throw err
    }
  }, [apiCall, fetchStocks])

  return {
    stocks,
    shariahStocks,
    fetchStocks,
    refreshStockPrices,
    loading,
    error
  }
}

export function useSignals() {
  const { apiCall, loading, error } = useApi()
  const [signals, setSignals] = useState([])
  const [todaySignals, setTodaySignals] = useState([])
  const [openSignals, setOpenSignals] = useState([])

  const generateSignals = useCallback(async (options = {}) => {
    try {
      const {
        strategy = 'multibagger',
        symbols = null,
        shariah_only = true,
        min_confidence = 0.7
      } = options

      const data = await apiCall('/signals/generate', {
        method: 'POST',
        body: {
          strategy,
          symbols,
          shariah_only,
          min_confidence
        }
      })

      if (data.success) {
        const signalData = data.signals || data.data?.signals || []
        setSignals(signalData)
        return signalData
      } else {
        throw new Error(data.error || 'Failed to generate signals')
      }
    } catch (err) {
      console.error('Error generating signals:', err)
      throw err
    }
  }, [apiCall])

  const fetchTodaySignals = useCallback(async () => {
    try {
      const data = await apiCall('/signals/today')
      if (data.success) {
        const signalData = data.signals || data.data?.signals || []
        setTodaySignals(signalData)
        return signalData
      }
    } catch (err) {
      console.error('Error fetching today signals:', err)
      throw err
    }
  }, [apiCall])

  const fetchOpenSignals = useCallback(async () => {
    try {
      const data = await apiCall('/signals/open')
      if (data.success) {
        const signalData = data.signals || data.data?.signals || []
        setOpenSignals(signalData)
        return signalData
      }
    } catch (err) {
      console.error('Error fetching open signals:', err)
      throw err
    }
  }, [apiCall])

  const trackSignals = useCallback(async (signalIds) => {
    try {
      const data = await apiCall('/signals/track', {
        method: 'POST',
        body: { signal_ids: signalIds }
      })
      return data
    } catch (err) {
      console.error('Error tracking signals:', err)
      throw err
    }
  }, [apiCall])

  return {
    signals,
    todaySignals,
    openSignals,
    generateSignals,
    fetchTodaySignals,
    fetchOpenSignals,
    trackSignals,
    loading,
    error
  }
}

export function useStrategies() {
  const { apiCall, loading, error } = useApi()
  const [strategies, setStrategies] = useState([])

  const fetchStrategies = useCallback(async () => {
    try {
      const data = await apiCall('/strategies')
      if (data.strategies) {
        setStrategies(data.strategies)
        return data.strategies
      }
    } catch (err) {
      console.error('Error fetching strategies:', err)
      throw err
    }
  }, [apiCall])

  const runBacktest = useCallback(async (options = {}) => {
    try {
      const {
        strategy = 'multibagger',
        start_date = '2019-01-01',
        end_date = '2025-01-27',
        symbols = null
      } = options

      const data = await apiCall('/backtest', {
        method: 'POST',
        body: {
          strategy,
          start_date,
          end_date,
          symbols
        }
      })

      return data
    } catch (err) {
      console.error('Error running backtest:', err)
      throw err
    }
  }, [apiCall])

  return {
    strategies,
    fetchStrategies,
    runBacktest,
    loading,
    error
  }
}

export function usePerformance() {
  const { apiCall, loading, error } = useApi()
  const [performance, setPerformance] = useState(null)

  const fetchPerformance = useCallback(async (period = '30d') => {
    try {
      const data = await apiCall(`/performance/summary?period=${period}`)
      if (data.success) {
        const perfData = data.performance || data.data || {}
        setPerformance(perfData)
        return perfData
      }
    } catch (err) {
      console.error('Error fetching performance:', err)
      throw err
    }
  }, [apiCall])

  return {
    performance,
    fetchPerformance,
    loading,
    error
  }
}

export function useStockDetails() {
  const { apiCall, loading, error } = useApi()
  const [stockDetails, setStockDetails] = useState(null)

  const fetchStockDetails = useCallback(async (symbol) => {
    try {
      const data = await apiCall(`/stock/${symbol}`)
      if (data.success) {
        const stockData = data.stock || data.data || {}
        setStockDetails(stockData)
        return stockData
      }
    } catch (err) {
      console.error('Error fetching stock details:', err)
      throw err
    }
  }, [apiCall])

  return {
    stockDetails,
    fetchStockDetails,
    loading,
    error
  }
}

// Health check hook
export function useHealthCheck() {
  const { apiCall } = useApi()
  const [isHealthy, setIsHealthy] = useState(null)
  const [lastCheck, setLastCheck] = useState(null)

  const checkHealth = useCallback(async () => {
    try {
      const data = await apiCall('/health')
      const healthy = data.status === 'healthy'
      setIsHealthy(healthy)
      setLastCheck(new Date())
      return healthy
    } catch (err) {
      setIsHealthy(false)
      setLastCheck(new Date())
      return false
    }
  }, [apiCall])

  // Auto health check on mount
  useEffect(() => {
    checkHealth()
    
    // Check health every 5 minutes
    const interval = setInterval(checkHealth, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [checkHealth])

  return {
    isHealthy,
    lastCheck,
    checkHealth
  }
}

// Utility function for error handling
export function handleApiError(error, setError) {
  console.error('API Error:', error)
  
  let errorMessage = 'An unexpected error occurred'
  
  if (error.message.includes('timeout')) {
    errorMessage = 'Request timeout. Please try again.'
  } else if (error.message.includes('HTTP 404')) {
    errorMessage = 'Resource not found.'
  } else if (error.message.includes('HTTP 500')) {
    errorMessage = 'Server error. Please try again later.'
  } else if (error.message.includes('Failed to fetch')) {
    errorMessage = 'Unable to connect to server. Please check your connection.'
  } else if (error.message) {
    errorMessage = error.message
  }
  
  if (setError) {
    setError(errorMessage)
  }
  
  return errorMessage
}
