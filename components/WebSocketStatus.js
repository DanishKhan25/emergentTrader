'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Wifi, WifiOff, RotateCcw, Activity } from 'lucide-react'
import { useWebSocket } from '@/contexts/WebSocketContext'

export default function WebSocketStatus() {
  const { 
    isConnected, 
    connectionStatus, 
    connect, 
    disconnect,
    reconnectAttempts,
    maxReconnectAttempts 
  } = useWebSocket()

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'bg-green-500'
      case 'connecting':
      case 'reconnecting':
        return 'bg-yellow-500'
      case 'disconnected':
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected'
      case 'connecting':
        return 'Connecting...'
      case 'reconnecting':
        return `Reconnecting... (${reconnectAttempts}/${maxReconnectAttempts})`
      case 'disconnected':
        return 'Disconnected'
      case 'error':
        return 'Connection Error'
      default:
        return 'Unknown'
    }
  }

  const getIcon = () => {
    if (isConnected) {
      return <Wifi className="h-3 w-3" />
    } else if (connectionStatus === 'connecting' || connectionStatus === 'reconnecting') {
      return <RotateCcw className="h-3 w-3 animate-spin" />
    } else {
      return <WifiOff className="h-3 w-3" />
    }
  }

  return (
    <div className="flex items-center gap-2">
      <Badge 
        variant="secondary" 
        className={`${getStatusColor()} text-white border-0 flex items-center gap-1`}
      >
        {getIcon()}
        <span className="text-xs">{getStatusText()}</span>
      </Badge>
      
      {!isConnected && connectionStatus !== 'connecting' && connectionStatus !== 'reconnecting' && (
        <Button
          variant="ghost"
          size="sm"
          onClick={connect}
          className="h-6 px-2 text-xs"
        >
          <Activity className="h-3 w-3 mr-1" />
          Reconnect
        </Button>
      )}
    </div>
  )
}
