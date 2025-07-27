'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

export function useRealTimeMarketRegime() {
  const [marketRegime, setMarketRegime] = useState(null)
  const [marketStatus, setMarketStatus] = useState(null)
  const [intradayData, setIntradayData] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [lastUpdate, setLastUpdate] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    try {
      setConnectionStatus('connecting')
      setError(null)

      // Create WebSocket connection
      const ws = new WebSocket('ws://localhost:8000/ws/market-regime')
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected to market regime service')
        setConnectionStatus('connected')
        setError(null)
        reconnectAttempts.current = 0
        setLoading(false)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        } catch (err) {
          console.error('Error parsing WebSocket message:', err)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason)
        setConnectionStatus('disconnected')
        
        // Attempt to reconnect if not intentionally closed
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
          console.log(`Attempting to reconnect in ${delay}ms...`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++
            connect()
          }, delay)
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setError('Failed to connect after multiple attempts')
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setError('WebSocket connection error')
        setConnectionStatus('error')
      }

    } catch (err) {
      console.error('Error creating WebSocket connection:', err)
      setError('Failed to create WebSocket connection')
      setConnectionStatus('error')
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected')
      wsRef.current = null
    }
    
    setConnectionStatus('disconnected')
  }, [])

  const handleWebSocketMessage = useCallback((data) => {
    const { type, timestamp } = data
    setLastUpdate(timestamp)

    switch (type) {
      case 'initial_data':
        if (data.regime) {
          setMarketRegime(data.regime)
        }
        if (data.market_status) {
          setMarketStatus(data.market_status)
        }
        setLoading(false)
        break

      case 'regime_update':
        if (data.regime) {
          setMarketRegime(data.regime)
          console.log('Market regime updated:', data.regime.regime, `(${(data.regime.confidence * 100).toFixed(1)}%)`)
        }
        break

      case 'market_data_update':
        if (data.current_snapshot) {
          setMarketStatus(prevStatus => ({
            ...prevStatus,
            current_snapshot: data.current_snapshot
          }))
        }
        if (data.market_status) {
          setMarketStatus(prevStatus => ({
            ...prevStatus,
            ...data.market_status
          }))
        }
        break

      case 'intraday_update':
        if (data.regime) {
          setMarketRegime(data.regime)
        }
        if (data.intraday_data) {
          setIntradayData(data.intraday_data)
        }
        break

      case 'pong':
        // Handle ping response
        break

      default:
        console.log('Unknown WebSocket message type:', type)
    }
  }, [])

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  const requestUpdate = useCallback(() => {
    sendMessage({ type: 'request_update' })
  }, [sendMessage])

  const ping = useCallback(() => {
    sendMessage({ type: 'ping' })
  }, [sendMessage])

  // Fallback to REST API if WebSocket fails
  const fetchFallbackData = useCallback(async () => {
    try {
      setLoading(true)
      
      // Fetch regime data
      const regimeResponse = await fetch('http://localhost:8000/market-regime/summary-realtime')
      const regimeData = await regimeResponse.json()
      
      if (regimeData.success) {
        setMarketRegime({
          regime: regimeData.data.current_regime,
          confidence: regimeData.data.confidence,
          description: regimeData.data.description,
          indicators: regimeData.data.indicators,
          timestamp: regimeData.data.last_update
        })
        
        if (regimeData.data.market_status) {
          setMarketStatus(regimeData.data.market_status)
        }
      }
      
      setError(null)
    } catch (err) {
      console.error('Error fetching fallback data:', err)
      setError('Failed to fetch market regime data')
    } finally {
      setLoading(false)
    }
  }, [])

  // Initialize connection
  useEffect(() => {
    connect()

    // Cleanup on unmount
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  // Ping interval to keep connection alive
  useEffect(() => {
    if (connectionStatus === 'connected') {
      const pingInterval = setInterval(() => {
        ping()
      }, 30000) // Ping every 30 seconds

      return () => clearInterval(pingInterval)
    }
  }, [connectionStatus, ping])

  // Fallback to REST API if WebSocket fails
  useEffect(() => {
    if (connectionStatus === 'error' || (connectionStatus === 'disconnected' && reconnectAttempts.current >= maxReconnectAttempts)) {
      console.log('Using REST API fallback for market regime data')
      fetchFallbackData()
      
      // Set up polling as fallback
      const pollInterval = setInterval(fetchFallbackData, 60000) // Poll every minute
      
      return () => clearInterval(pollInterval)
    }
  }, [connectionStatus, fetchFallbackData])

  return {
    // Data
    marketRegime,
    marketStatus,
    intradayData,
    
    // Status
    connectionStatus,
    lastUpdate,
    error,
    loading,
    
    // Actions
    requestUpdate,
    ping,
    connect,
    disconnect,
    
    // Computed values
    isConnected: connectionStatus === 'connected',
    isMarketOpen: marketStatus?.is_open || false,
    regimeConfidence: marketRegime?.confidence || 0,
    currentRegime: marketRegime?.regime || 'unknown'
  }
}

// Hook for simplified market regime data (without WebSocket complexity)
export function useMarketRegime() {
  const [regime, setRegime] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)

  const fetchRegime = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('http://localhost:8000/market-regime/summary-realtime')
      const data = await response.json()
      
      if (data.success) {
        setRegime(data.data)
        setLastUpdate(new Date().toISOString())
      } else {
        setError(data.error || 'Failed to fetch market regime')
      }
    } catch (err) {
      console.error('Error fetching market regime:', err)
      setError('Network error while fetching market regime')
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial fetch
  useEffect(() => {
    fetchRegime()
  }, [fetchRegime])

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(fetchRegime, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [fetchRegime])

  return {
    regime,
    loading,
    error,
    lastUpdate,
    refresh: fetchRegime,
    
    // Computed values
    currentRegime: regime?.current_regime || 'unknown',
    confidence: regime?.confidence || 0,
    description: regime?.description || '',
    isMarketOpen: regime?.market_status?.is_open || false
  }
}

// Hook for real-time strategy filtering
export function useRealTimeStrategyFilter(strategies = []) {
  const [filteredStrategies, setFilteredStrategies] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const filterStrategies = useCallback(async () => {
    if (!strategies.length) return

    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('http://localhost:8000/market-regime/filter-strategies-realtime', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategies })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setFilteredStrategies(data.data)
      } else {
        setError(data.error || 'Failed to filter strategies')
      }
    } catch (err) {
      console.error('Error filtering strategies:', err)
      setError('Network error while filtering strategies')
    } finally {
      setLoading(false)
    }
  }, [strategies])

  useEffect(() => {
    filterStrategies()
  }, [filterStrategies])

  return {
    filteredStrategies,
    loading,
    error,
    refresh: filterStrategies,
    
    // Computed values
    recommendedStrategies: filteredStrategies?.recommendations?.use || [],
    cautionStrategies: filteredStrategies?.recommendations?.caution || [],
    avoidStrategies: filteredStrategies?.recommendations?.avoid || []
  }
}

export default useRealTimeMarketRegime
