'use client'

import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react'
import apiService from '@/lib/api'

// Initial state
const initialState = {
  // System status
  isConnected: false,
  isLoading: false,
  error: null,
  lastUpdate: null,

  // Stock data
  stocks: [],
  shariahStocks: [],
  selectedStock: null,

  // Signals
  todaySignals: [],
  openSignals: [],
  signalHistory: [],

  // Performance data
  performance: null,
  portfolio: null,
  analytics: null,

  // System data
  systemHealth: null,
  systemStatus: null,

  // Strategies
  strategies: [],

  // Settings
  settings: {
    autoRefresh: true,
    refreshInterval: 30000,
    shariahOnly: false,
    notifications: true
  }
}

// Action types
const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_CONNECTED: 'SET_CONNECTED',
  UPDATE_STOCKS: 'UPDATE_STOCKS',
  UPDATE_SHARIAH_STOCKS: 'UPDATE_SHARIAH_STOCKS',
  SET_SELECTED_STOCK: 'SET_SELECTED_STOCK',
  UPDATE_TODAY_SIGNALS: 'UPDATE_TODAY_SIGNALS',
  UPDATE_OPEN_SIGNALS: 'UPDATE_OPEN_SIGNALS',
  UPDATE_SIGNAL_HISTORY: 'UPDATE_SIGNAL_HISTORY',
  UPDATE_PERFORMANCE: 'UPDATE_PERFORMANCE',
  UPDATE_PORTFOLIO: 'UPDATE_PORTFOLIO',
  UPDATE_ANALYTICS: 'UPDATE_ANALYTICS',
  UPDATE_SYSTEM_HEALTH: 'UPDATE_SYSTEM_HEALTH',
  UPDATE_SYSTEM_STATUS: 'UPDATE_SYSTEM_STATUS',
  UPDATE_STRATEGIES: 'UPDATE_STRATEGIES',
  UPDATE_SETTINGS: 'UPDATE_SETTINGS',
  SET_LAST_UPDATE: 'SET_LAST_UPDATE',
  CLEAR_ERROR: 'CLEAR_ERROR'
}

// Reducer
function dataReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return { ...state, isLoading: action.payload }
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, isLoading: false }
    
    case ActionTypes.SET_CONNECTED:
      return { ...state, isConnected: action.payload }
    
    case ActionTypes.UPDATE_STOCKS:
      return { ...state, stocks: action.payload }
    
    case ActionTypes.UPDATE_SHARIAH_STOCKS:
      return { ...state, shariahStocks: action.payload }
    
    case ActionTypes.SET_SELECTED_STOCK:
      return { ...state, selectedStock: action.payload }
    
    case ActionTypes.UPDATE_TODAY_SIGNALS:
      return { ...state, todaySignals: action.payload }
    
    case ActionTypes.UPDATE_OPEN_SIGNALS:
      return { ...state, openSignals: action.payload }
    
    case ActionTypes.UPDATE_SIGNAL_HISTORY:
      return { ...state, signalHistory: action.payload }
    
    case ActionTypes.UPDATE_PERFORMANCE:
      return { ...state, performance: action.payload }
    
    case ActionTypes.UPDATE_PORTFOLIO:
      return { ...state, portfolio: action.payload }
    
    case ActionTypes.UPDATE_ANALYTICS:
      return { ...state, analytics: action.payload }
    
    case ActionTypes.UPDATE_SYSTEM_HEALTH:
      return { ...state, systemHealth: action.payload }
    
    case ActionTypes.UPDATE_SYSTEM_STATUS:
      return { ...state, systemStatus: action.payload }
    
    case ActionTypes.UPDATE_STRATEGIES:
      return { ...state, strategies: action.payload }
    
    case ActionTypes.UPDATE_SETTINGS:
      return { ...state, settings: { ...state.settings, ...action.payload } }
    
    case ActionTypes.SET_LAST_UPDATE:
      return { ...state, lastUpdate: action.payload }
    
    case ActionTypes.CLEAR_ERROR:
      return { ...state, error: null }
    
    default:
      return state
  }
}

// Create context
const DataContext = createContext()

// Provider component
export function DataProvider({ children }) {
  const [state, dispatch] = useReducer(dataReducer, initialState)

  // Error handler
  const handleError = useCallback((error) => {
    console.error('Data Context Error:', error)
    dispatch({ type: ActionTypes.SET_ERROR, payload: error.message })
  }, [])

  // Clear error
  const clearError = useCallback(() => {
    dispatch({ type: ActionTypes.CLEAR_ERROR })
  }, [])

  // Load initial data
  const loadInitialData = useCallback(async () => {
    dispatch({ type: ActionTypes.SET_LOADING, payload: true })
    
    try {
      // Load all initial data in parallel
      const [
        stocksResponse,
        shariahResponse,
        todaySignalsResponse,
        openSignalsResponse,
        performanceResponse,
        portfolioResponse,
        strategiesResponse,
        systemHealthResponse
      ] = await Promise.allSettled([
        apiService.getStocks(false, true, 200), // All stocks with prices, limited to 200 for performance
        apiService.getStocks(true, true), // Shariah stocks with prices
        apiService.getTodaySignals(),
        apiService.getOpenSignals(),
        apiService.getPerformanceSummary(),
        apiService.getPortfolioData(),
        apiService.getStrategies(),
        apiService.getSystemHealth()
      ])

      // Update state with successful responses
      if (stocksResponse.status === 'fulfilled' && stocksResponse.value.success) {
        dispatch({ type: ActionTypes.UPDATE_STOCKS, payload: stocksResponse.value.data?.stocks || [] })
      }

      if (shariahResponse.status === 'fulfilled' && shariahResponse.value.success) {
        dispatch({ type: ActionTypes.UPDATE_SHARIAH_STOCKS, payload: shariahResponse.value.data?.stocks || [] })
      }

      if (todaySignalsResponse.status === 'fulfilled' && todaySignalsResponse.value.success) {
        dispatch({ type: ActionTypes.UPDATE_TODAY_SIGNALS, payload: todaySignalsResponse.value.data?.signals || [] })
      }

      if (openSignalsResponse.status === 'fulfilled' && openSignalsResponse.value.success) {
        dispatch({ type: ActionTypes.UPDATE_OPEN_SIGNALS, payload: openSignalsResponse.value.data?.signals || [] })
      }

      if (performanceResponse.status === 'fulfilled' && performanceResponse.value.success) {
        dispatch({ type: ActionTypes.UPDATE_PERFORMANCE, payload: performanceResponse.value.data || null })
      }

      if (portfolioResponse.status === 'fulfilled' && portfolioResponse.value.success) {
        dispatch({ type: ActionTypes.UPDATE_PORTFOLIO, payload: portfolioResponse.value.data || null })
      }

      if (strategiesResponse.status === 'fulfilled' && strategiesResponse.value.strategies) {
        dispatch({ type: ActionTypes.UPDATE_STRATEGIES, payload: strategiesResponse.value.strategies })
      }

      if (systemHealthResponse.status === 'fulfilled') {
        dispatch({ type: ActionTypes.UPDATE_SYSTEM_HEALTH, payload: systemHealthResponse.value })
        dispatch({ type: ActionTypes.SET_CONNECTED, payload: systemHealthResponse.value.status === 'healthy' })
      }

      dispatch({ type: ActionTypes.SET_LAST_UPDATE, payload: new Date() })
      
    } catch (error) {
      handleError(error)
    } finally {
      dispatch({ type: ActionTypes.SET_LOADING, payload: false })
    }
  }, [handleError])

  // Refresh data
  const refreshData = useCallback(async (dataTypes = []) => {
    try {
      const refreshPromises = []

      if (dataTypes.length === 0 || dataTypes.includes('stocks')) {
        refreshPromises.push(
          apiService.getStocks(false, true, 200).then(response => {
            if (response.success) {
              dispatch({ type: ActionTypes.UPDATE_STOCKS, payload: response.data?.stocks || [] })
            }
          })
        )

        refreshPromises.push(
          apiService.getStocks(true, true).then(response => {
            if (response.success) {
              dispatch({ type: ActionTypes.UPDATE_SHARIAH_STOCKS, payload: response.data?.stocks || [] })
            }
          })
        )
      }

      if (dataTypes.length === 0 || dataTypes.includes('signals')) {
        refreshPromises.push(
          apiService.getTodaySignals().then(response => {
            if (response.success) {
              dispatch({ type: ActionTypes.UPDATE_TODAY_SIGNALS, payload: response.data?.signals || [] })
            }
          }),
          apiService.getOpenSignals().then(response => {
            if (response.success) {
              dispatch({ type: ActionTypes.UPDATE_OPEN_SIGNALS, payload: response.data?.signals || [] })
            }
          })
        )
      }

      if (dataTypes.length === 0 || dataTypes.includes('performance')) {
        refreshPromises.push(
          apiService.getPerformanceSummary().then(response => {
            if (response.success) {
              dispatch({ type: ActionTypes.UPDATE_PERFORMANCE, payload: response.data || null })
            }
          })
        )
      }

      if (dataTypes.length === 0 || dataTypes.includes('health')) {
        refreshPromises.push(
          apiService.getSystemHealth().then(response => {
            dispatch({ type: ActionTypes.UPDATE_SYSTEM_HEALTH, payload: response })
            dispatch({ type: ActionTypes.SET_CONNECTED, payload: response.status === 'healthy' })
          })
        )
      }

      await Promise.allSettled(refreshPromises)
      dispatch({ type: ActionTypes.SET_LAST_UPDATE, payload: new Date() })

    } catch (error) {
      handleError(error)
    }
  }, [handleError])

  // Generate signals
  const generateSignals = useCallback(async (options = {}) => {
    dispatch({ type: ActionTypes.SET_LOADING, payload: true })
    
    try {
      const response = await apiService.generateSignals(options)
      
      if (response.success) {
        // Refresh signals after generation
        await refreshData(['signals'])
        return response.data
      } else {
        throw new Error(response.error || 'Failed to generate signals')
      }
    } catch (error) {
      handleError(error)
      throw error
    } finally {
      dispatch({ type: ActionTypes.SET_LOADING, payload: false })
    }
  }, [handleError, refreshData])

  // Update settings
  const updateSettings = useCallback((newSettings) => {
    dispatch({ type: ActionTypes.UPDATE_SETTINGS, payload: newSettings })
    
    // Save to localStorage
    try {
      localStorage.setItem('emergentTrader_settings', JSON.stringify({
        ...state.settings,
        ...newSettings
      }))
    } catch (error) {
      console.warn('Failed to save settings to localStorage:', error)
    }
  }, [state.settings])

  // Load settings from localStorage
  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('emergentTrader_settings')
      if (savedSettings) {
        const settings = JSON.parse(savedSettings)
        dispatch({ type: ActionTypes.UPDATE_SETTINGS, payload: settings })
      }
    } catch (error) {
      console.warn('Failed to load settings from localStorage:', error)
    }
  }, [])

  // Auto refresh functionality
  useEffect(() => {
    if (!state.settings.autoRefresh) return

    const interval = setInterval(() => {
      refreshData()
    }, state.settings.refreshInterval)

    return () => clearInterval(interval)
  }, [state.settings.autoRefresh, state.settings.refreshInterval, refreshData])

  // Real-time updates via WebSocket
  useEffect(() => {
    let ws = null

    const connectWebSocket = () => {
      ws = apiService.connectWebSocket(
        (data) => {
          // Handle real-time updates
          switch (data.type) {
            case 'signal_update':
              refreshData(['signals'])
              break
            case 'price_update':
              refreshData(['stocks'])
              break
            case 'system_status':
              dispatch({ type: ActionTypes.UPDATE_SYSTEM_STATUS, payload: data.payload })
              break
            default:
              console.log('Unknown WebSocket message:', data)
          }
        },
        (error) => {
          console.error('WebSocket error:', error)
          dispatch({ type: ActionTypes.SET_CONNECTED, payload: false })
        }
      )
    }

    // Connect WebSocket if supported
    if (typeof WebSocket !== 'undefined') {
      connectWebSocket()
    }

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [refreshData])

  // Load initial data on mount
  useEffect(() => {
    loadInitialData()
  }, [loadInitialData])

  // Context value
  const contextValue = {
    // State
    ...state,
    
    // Actions
    loadInitialData,
    refreshData,
    generateSignals,
    updateSettings,
    clearError,
    
    // Utilities
    setSelectedStock: (stock) => dispatch({ type: ActionTypes.SET_SELECTED_STOCK, payload: stock }),
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading })
  }

  return (
    <DataContext.Provider value={contextValue}>
      {children}
    </DataContext.Provider>
  )
}

// Hook to use the context
export function useData() {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useData must be used within a DataProvider')
  }
  return context
}

export default DataContext
