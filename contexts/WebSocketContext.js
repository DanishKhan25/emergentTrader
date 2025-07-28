'use client'

import { createContext, useContext, useEffect, useState, useRef } from 'react'
import { useNotifications } from '@/components/notifications/NotificationProvider'

const WebSocketContext = createContext()

export const useWebSocket = () => {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

export default function WebSocketProvider({ children }) {
  const [socket, setSocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [lastMessage, setLastMessage] = useState(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const reconnectDelay = 3000

  const { addNotification, notifySignalGenerated, notifyPriceAlert } = useNotifications()

  const connect = () => {
    try {
      setConnectionStatus('connecting')
      
      // Connect to Python backend WebSocket
      const ws = new WebSocket('ws://localhost:8000/ws')
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setSocket(ws)
        setIsConnected(true)
        setConnectionStatus('connected')
        reconnectAttempts.current = 0
        
        // Send connection confirmation
        ws.send(JSON.stringify({
          type: 'connection',
          message: 'Frontend connected'
        }))
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          handleMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setSocket(null)
        setIsConnected(false)
        setConnectionStatus('disconnected')
        
        // Attempt to reconnect if not a manual close
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          scheduleReconnect()
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('error')
      }

    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      setConnectionStatus('error')
      scheduleReconnect()
    }
  }

  const scheduleReconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    reconnectAttempts.current += 1
    setConnectionStatus('reconnecting')
    
    console.log(`Attempting to reconnect... (${reconnectAttempts.current}/${maxReconnectAttempts})`)
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connect()
    }, reconnectDelay * reconnectAttempts.current)
  }

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (socket) {
      socket.close(1000, 'Manual disconnect')
    }
    
    setSocket(null)
    setIsConnected(false)
    setConnectionStatus('disconnected')
  }

  const sendMessage = (message) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message))
      return true
    } else {
      console.warn('WebSocket not connected. Message not sent:', message)
      return false
    }
  }

  const handleMessage = (data) => {
    console.log('WebSocket message received:', data)
    
    switch (data.type) {
      case 'signal_generated':
        handleSignalGenerated(data.data)
        break
      
      case 'price_alert':
        handlePriceAlert(data.data)
        break
      
      case 'target_hit':
        handleTargetHit(data.data)
        break
      
      case 'stop_loss_hit':
        handleStopLossHit(data.data)
        break
      
      case 'portfolio_update':
        handlePortfolioUpdate(data.data)
        break
      
      case 'system_status':
        handleSystemStatus(data.data)
        break
      
      case 'heartbeat':
        // Handle heartbeat to keep connection alive
        sendMessage({ type: 'heartbeat_response', timestamp: Date.now() })
        break
      
      default:
        console.log('Unknown message type:', data.type)
    }
  }

  const handleSignalGenerated = (signalData) => {
    // Show notification
    notifySignalGenerated(signalData)
    
    // Broadcast to other components
    window.dispatchEvent(new CustomEvent('signalGenerated', { detail: signalData }))
  }

  const handlePriceAlert = (alertData) => {
    notifyPriceAlert(alertData)
    window.dispatchEvent(new CustomEvent('priceAlert', { detail: alertData }))
  }

  const handleTargetHit = (targetData) => {
    addNotification({
      type: 'success',
      title: 'Target Hit! 🎯',
      message: `${targetData.symbol} reached target price of ₹${targetData.target_price}`,
      data: targetData,
      duration: 10000
    })
    
    window.dispatchEvent(new CustomEvent('targetHit', { detail: targetData }))
  }

  const handleStopLossHit = (stopLossData) => {
    addNotification({
      type: 'error',
      title: 'Stop Loss Triggered',
      message: `${stopLossData.symbol} hit stop loss at ₹${stopLossData.stop_loss}`,
      data: stopLossData,
      duration: 10000
    })
    
    window.dispatchEvent(new CustomEvent('stopLossHit', { detail: stopLossData }))
  }

  const handlePortfolioUpdate = (portfolioData) => {
    addNotification({
      type: 'portfolio',
      title: 'Portfolio Update',
      message: portfolioData.message,
      data: portfolioData
    })
    
    window.dispatchEvent(new CustomEvent('portfolioUpdate', { detail: portfolioData }))
  }

  const handleSystemStatus = (statusData) => {
    console.log('System status update:', statusData)
    window.dispatchEvent(new CustomEvent('systemStatus', { detail: statusData }))
  }

  // Auto-connect on mount
  useEffect(() => {
    connect()
    
    return () => {
      disconnect()
    }
  }, [])

  // Heartbeat to keep connection alive
  useEffect(() => {
    if (!isConnected) return

    const heartbeatInterval = setInterval(() => {
      sendMessage({ 
        type: 'heartbeat', 
        timestamp: Date.now() 
      })
    }, 30000) // Send heartbeat every 30 seconds

    return () => clearInterval(heartbeatInterval)
  }, [isConnected])

  const value = {
    socket,
    isConnected,
    connectionStatus,
    lastMessage,
    connect,
    disconnect,
    sendMessage,
    reconnectAttempts: reconnectAttempts.current,
    maxReconnectAttempts
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}
