'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  TrendingUp, 
  TrendingDown, 
  Target,
  Shield,
  Clock,
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  BarChart3,
  Calendar,
  DollarSign,
  Trash2
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useWebSocket } from '@/contexts/WebSocketContext'
import { useNotifications } from '@/components/notifications/NotificationProvider'

export default function SignalsPage() {
  const [signals, setSignals] = useState([])
  const [activeSignals, setActiveSignals] = useState([])
  const [signalStats, setSignalStats] = useState({})
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [selectedStrategy, setSelectedStrategy] = useState('multibagger')
  const [minConfidence, setMinConfidence] = useState(0.7)
  const [showDialog, setShowDialog] = useState(false)
  const [marketDataAvailable, setMarketDataAvailable] = useState(true)
  
  const { getAuthHeaders } = useAuth()
  const { isConnected, lastMessage } = useWebSocket()
  const { addNotification } = useNotifications()

  // Load data on component mount
  useEffect(() => {
    loadSignalData()
  }, [])

  // Listen for real-time WebSocket updates
  useEffect(() => {
    if (lastMessage) {
      switch (lastMessage.type) {
        case 'signal_generated':
          handleNewSignal(lastMessage.data)
          break
        case 'target_hit':
          handleTargetHit(lastMessage.data)
          break
        case 'stop_loss_hit':
          handleStopLoss(lastMessage.data)
          break
        case 'signals_cleared':
          loadSignalData() // Refresh all data
          break
        default:
          break
      }
    }
  }, [lastMessage])

  const processSignalData = (signal) => {
    // Parse metadata if it exists and is a string
    let metadata = {}
    if (signal.metadata && typeof signal.metadata === 'string') {
      try {
        metadata = JSON.parse(signal.metadata)
      } catch (e) {
        console.warn('Failed to parse signal metadata:', e)
      }
    } else if (signal.metadata && typeof signal.metadata === 'object') {
      metadata = signal.metadata
    }

    // Calculate days active
    const createdAt = new Date(signal.generated_at || signal.created_at || Date.now())
    const now = new Date()
    const daysActive = Math.floor((now - createdAt) / (1000 * 60 * 60 * 24))

    // Get current price (try multiple sources)
    const currentPrice = signal.current_price || signal.price || signal.entry_price || metadata.entry_price || 0
    const entryPrice = signal.entry_price || metadata.entry_price || currentPrice
    
    // Calculate unrealized P&L if we have both prices
    let unrealizedPnlPercent = 0
    if (currentPrice && entryPrice && entryPrice > 0) {
      unrealizedPnlPercent = ((currentPrice - entryPrice) / entryPrice) * 100
    }

    // Get confidence (try multiple sources)
    const confidence = signal.confidence || signal.confidence_score || metadata.confidence_score || 0

    // Process the signal with standardized field names
    return {
      ...signal,
      // Standardized fields
      signal_id: signal.signal_id || signal.id,
      symbol: signal.symbol,
      strategy: signal.strategy,
      signal_type: signal.signal_type || 'BUY',
      entry_price: entryPrice,
      current_price: currentPrice,
      target_price: signal.target_price || metadata.target_price || 0,
      stop_loss: signal.stop_loss || metadata.stop_loss || 0,
      confidence: confidence,
      status: (signal.status || 'ACTIVE').toLowerCase(),
      
      // Calculated fields
      days_active: daysActive,
      unrealized_pnl_percent: unrealizedPnlPercent,
      
      // Additional metadata fields
      sector: metadata.sector || signal.sector || 'Unknown',
      market_cap: metadata.market_cap || signal.market_cap,
      risk_reward_ratio: metadata.risk_reward_ratio || signal.risk_reward_ratio,
      strategy_reason: metadata.strategy_reason || signal.strategy_reason,
      investment_thesis: metadata.investment_thesis || signal.investment_thesis,
      shariah_compliant: metadata.shariah_compliant || signal.shariah_compliant || false,
      
      // Technical indicators
      rsi: metadata.rsi || signal.rsi,
      momentum_score: metadata.momentum_score || signal.momentum_score,
      volume_ratio: metadata.volume_ratio || signal.volume_ratio,
      
      // Timestamps
      created_at: signal.generated_at || signal.created_at,
      updated_at: signal.updated_at
    }
  }

  const loadSignalData = async () => {
    try {
      setLoading(true)
      
      // Define backend URL
      const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Load signals and active signals in parallel
      const [signalsResponse, activeResponse] = await Promise.all([
        fetch(`${BACKEND_URL}/signals`, { 
          headers: { 
            'Content-Type': 'application/json',
            ...getAuthHeaders() 
          } 
        }),
        fetch(`${BACKEND_URL}/signals/active`, { 
          headers: { 
            'Content-Type': 'application/json',
            ...getAuthHeaders() 
          } 
        })
      ])

      // Handle signals response
      if (signalsResponse.ok) {
        const signalsData = await signalsResponse.json()
        if (signalsData.success) {
          const rawSignals = signalsData.data?.signals || signalsData.signals || []
          const processedSignals = rawSignals.map(processSignalData)
          setSignals(processedSignals)
          setMarketDataAvailable(true)
        } else {
          console.warn('Signals API not available, using fallback')
          setMarketDataAvailable(false)
        }
      } else {
        console.warn(`Signals API returned ${signalsResponse.status}`)
        setMarketDataAvailable(false)
      }

      // Handle active signals response
      if (activeResponse.ok) {
        const activeData = await activeResponse.json()
        if (activeData.success) {
          const rawActiveSignals = activeData.data?.signals || activeData.signals || []
          const processedActiveSignals = rawActiveSignals.map(processSignalData)
          setActiveSignals(processedActiveSignals)
        }
      } else {
        console.warn(`Active signals API returned ${activeResponse.status}`)
      }

      // Calculate basic statistics from the loaded data
      calculateBasicStats()

    } catch (error) {
      console.error('Error loading signal data:', error)
      setMarketDataAvailable(false)
      
      // Show user-friendly notification
      addNotification({
        type: 'warning',
        title: 'Backend Connection',
        message: 'Unable to connect to trading backend. Please ensure the Python backend is running on port 8000.',
        duration: 8000
      })
    } finally {
      setLoading(false)
    }
  }

  const calculateBasicStats = () => {
    // Calculate basic statistics from loaded signals
    const totalSignals = signals.length
    const activeCount = activeSignals.length
    
    // Count target hits and stop losses from signal status
    let targetHits = 0
    let stopLosses = 0
    
    signals.forEach(signal => {
      if (signal.status === 'target_hit' || signal.status === 'completed') {
        targetHits++
      } else if (signal.status === 'stop_loss_hit' || signal.status === 'stopped') {
        stopLosses++
      }
    })
    
    const successRate = totalSignals > 0 ? (targetHits / totalSignals) * 100 : 0
    
    // Group by strategy
    const strategyStats = {}
    signals.forEach(signal => {
      const strategy = signal.strategy || 'unknown'
      if (!strategyStats[strategy]) {
        strategyStats[strategy] = {
          strategy,
          total: 0,
          target_hits: 0,
          stop_losses: 0,
          success_rate: 0,
          avg_profit_percent: 0
        }
      }
      
      strategyStats[strategy].total++
      if (signal.status === 'target_hit' || signal.status === 'completed') {
        strategyStats[strategy].target_hits++
      } else if (signal.status === 'stop_loss_hit' || signal.status === 'stopped') {
        strategyStats[strategy].stop_losses++
      }
    })
    
    // Calculate success rates for strategies
    Object.values(strategyStats).forEach(stat => {
      stat.success_rate = stat.total > 0 ? (stat.target_hits / stat.total) * 100 : 0
    })
    
    setSignalStats({
      success: true,
      overall: {
        total_signals: totalSignals,
        active_signals: activeCount,
        target_hits: targetHits,
        stop_losses: stopLosses,
        success_rate: successRate,
        total_pnl: 0 // Would need price data to calculate
      },
      by_strategy: Object.values(strategyStats)
    })
  }

  const handleNewSignal = (signalData) => {
    // Add new signal to the list
    setSignals(prev => [signalData, ...prev])
    setActiveSignals(prev => [signalData, ...prev])
    
    // Show notification
    addNotification({
      type: 'success',
      title: 'New Signal Generated',
      message: `${signalData.symbol} - ${signalData.strategy} (${(signalData.confidence * 100).toFixed(0)}% confidence)`,
      duration: 8000
    })
    
    // Refresh statistics
    loadSignalStats()
  }

  const handleTargetHit = (targetData) => {
    // Update signal status
    setActiveSignals(prev => prev.filter(s => s.signal_id !== targetData.signal_id))
    
    // Show notification
    addNotification({
      type: 'success',
      title: 'Target Hit! 🎯',
      message: `${targetData.symbol} reached target price`,
      duration: 10000
    })
    
    // Refresh statistics
    loadSignalStats()
  }

  const handleStopLoss = (stopLossData) => {
    // Update signal status
    setActiveSignals(prev => prev.filter(s => s.signal_id !== stopLossData.signal_id))
    
    // Show notification
    addNotification({
      type: 'error',
      title: 'Stop Loss Hit',
      message: `${stopLossData.symbol} hit stop loss`,
      duration: 10000
    })
    
    // Refresh statistics
    loadSignalStats()
  }

  const loadSignalStats = async () => {
    // Since /signals/statistics doesn't exist, recalculate from loaded data
    calculateBasicStats()
  }

  const generateSignals = async () => {
    try {
      setGenerating(true)
      
      const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${BACKEND_URL}/signals/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify({
          strategy: selectedStrategy,
          min_confidence: minConfidence,
          shariah_only: true
        })
      })

      const result = await response.json()
      
      if (result.success) {
        addNotification({
          type: 'success',
          title: 'Signal Generation Started',
          message: 'New signals are being generated. You will be notified when complete.',
          duration: 5000
        })
        
        setShowDialog(false)
        
        // Refresh data after a short delay
        setTimeout(() => {
          loadSignalData()
        }, 2000)
      } else {
        addNotification({
          type: 'error',
          title: 'Generation Failed',
          message: result.error || 'Failed to generate signals. Please ensure the Python backend is running.',
          duration: 8000
        })
      }
    } catch (error) {
      console.error('Error generating signals:', error)
      addNotification({
        type: 'error',
        title: 'Connection Error',
        message: 'Unable to connect to backend. Please ensure the Python backend is running on port 8000.',
        duration: 8000
      })
    } finally {
      setGenerating(false)
    }
  }

  const clearAllSignals = async () => {
    try {
      const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Use DELETE method as per the API specification
      const response = await fetch(`${BACKEND_URL}/signals/clear`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      })

      const result = await response.json()
      
      if (result.success) {
        setSignals([])
        setActiveSignals([])
        setSignalStats({})
        
        addNotification({
          type: 'info',
          title: 'Signals Cleared',
          message: `Cleared signals from database`,
          duration: 5000
        })
      } else {
        addNotification({
          type: 'error',
          title: 'Clear Failed',
          message: result.error || 'Failed to clear signals',
          duration: 5000
        })
      }
    } catch (error) {
      console.error('Error clearing signals:', error)
      addNotification({
        type: 'error',
        title: 'Connection Error',
        message: 'Unable to connect to backend. Please ensure the Python backend is running on port 8000.',
        duration: 8000
      })
    }
  }

  const refreshData = async () => {
    setRefreshing(true)
    await loadSignalData()
    setRefreshing(false)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-blue-500'
      case 'target_hit': return 'bg-green-500'
      case 'stop_loss_hit': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Activity className="h-4 w-4" />
      case 'target_hit': return <CheckCircle className="h-4 w-4" />
      case 'stop_loss_hit': return <XCircle className="h-4 w-4" />
      default: return <AlertTriangle className="h-4 w-4" />
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount)
  }

  const formatPercent = (percent) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`
  }

  const overall = signalStats.overall || {}
  const byStrategy = signalStats.by_strategy || []

  if (loading) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="h-8 w-8 animate-spin" />
          </div>
        </MainLayout>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="space-y-6 p-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Trading Signals</h1>
              <p className="text-gray-600 mt-1">
                AI-powered trading signals with real-time tracking
                {!marketDataAvailable && (
                  <span className="ml-2 text-amber-600">
                    ⚠️ Market data service not available, using cached data
                  </span>
                )}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 text-sm">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span>{isConnected ? 'Live' : 'Offline'}</span>
              </div>
              <Button onClick={refreshData} disabled={refreshing} variant="outline">
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button onClick={clearAllSignals} variant="destructive" size="sm">
                <Trash2 className="h-4 w-4 mr-2" />
                Clear All
              </Button>
              <Button onClick={() => setShowDialog(true)}>
                <Target className="h-4 w-4 mr-2" />
                Generate Signals
              </Button>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{overall.total_signals || 0}</div>
                  <div className="text-sm text-gray-600">Total Signals</div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{overall.active_signals || 0}</div>
                  <div className="text-sm text-gray-600">Active</div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{overall.target_hits || 0}</div>
                  <div className="text-sm text-gray-600">Targets Hit</div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{overall.stop_losses || 0}</div>
                  <div className="text-sm text-gray-600">Stop Losses</div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{overall.success_rate?.toFixed(1) || 0}%</div>
                  <div className="text-sm text-gray-600">Success Rate</div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className={`text-2xl font-bold ${overall.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(overall.total_pnl || 0)}
                  </div>
                  <div className="text-sm text-gray-600">Total P&L</div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Tabs defaultValue="active" className="space-y-6">
            <TabsList>
              <TabsTrigger value="active">Active Signals ({activeSignals.length})</TabsTrigger>
              <TabsTrigger value="all">All Signals ({signals.length})</TabsTrigger>
              <TabsTrigger value="performance">Performance</TabsTrigger>
            </TabsList>

            {/* Active Signals Tab */}
            <TabsContent value="active" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Active Signals ({activeSignals.length})
                  </CardTitle>
                  <CardDescription>
                    Signals currently being tracked for target and stop loss
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {activeSignals.length === 0 ? (
                    <div className="text-center py-12">
                      <Target className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <h3 className="text-lg font-semibold text-gray-600 mb-2">No Active Signals</h3>
                      <p className="text-gray-500">Generate new signals to start tracking</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {activeSignals.map((signal) => (
                        <div key={signal.signal_id} className="border rounded-lg p-4 hover:bg-gray-50">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-semibold text-lg">{signal.symbol}</h4>
                                <Badge variant="secondary">{signal.strategy}</Badge>
                                <Badge className={getStatusColor(signal.status || 'active')}>
                                  {getStatusIcon(signal.status || 'active')}
                                  <span className="ml-1 capitalize">{(signal.status || 'active').replace('_', ' ')}</span>
                                </Badge>
                              </div>
                              
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div>
                                  <span className="text-gray-500">Entry Price:</span>
                                  <div className="font-medium">{formatCurrency(signal.entry_price)}</div>
                                </div>
                                <div>
                                  <span className="text-gray-500">Current Price:</span>
                                  <div className="font-medium">{formatCurrency(signal.current_price || signal.entry_price)}</div>
                                </div>
                                <div>
                                  <span className="text-gray-500">Target:</span>
                                  <div className="font-medium text-green-600">{formatCurrency(signal.target_price)}</div>
                                </div>
                                <div>
                                  <span className="text-gray-500">Stop Loss:</span>
                                  <div className="font-medium text-red-600">{formatCurrency(signal.stop_loss)}</div>
                                </div>
                              </div>
                              
                              <div className="mt-3 flex items-center gap-4">
                                <div className="flex items-center gap-2">
                                  <span className="text-sm text-gray-500">Confidence:</span>
                                  <span className="font-medium text-blue-600">
                                    {((signal.confidence || 0) * 100).toFixed(0)}%
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className="text-sm text-gray-500">Unrealized P&L:</span>
                                  <span className={`font-medium ${signal.unrealized_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {formatPercent(signal.unrealized_pnl_percent || 0)}
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Calendar className="h-4 w-4 text-gray-400" />
                                  <span className="text-sm text-gray-500">{signal.days_active || 0} days active</span>
                                </div>
                              </div>
                              
                              {/* Progress bar to target */}
                              <div className="mt-3">
                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                  <span>Stop Loss</span>
                                  <span>Target</span>
                                </div>
                                <Progress 
                                  value={
                                    ((signal.current_price || signal.entry_price) - signal.stop_loss) / 
                                    (signal.target_price - signal.stop_loss) * 100
                                  } 
                                  className="h-2"
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* All Signals Tab */}
            <TabsContent value="all" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>All Signals</CardTitle>
                  <CardDescription>Complete history of generated signals</CardDescription>
                </CardHeader>
                <CardContent>
                  {signals.length === 0 ? (
                    <div className="text-center py-12">
                      <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <h3 className="text-lg font-semibold text-gray-600 mb-2">No Signals Available</h3>
                      <p className="text-gray-500">Generate your first signals to get started</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {signals.slice(0, 10).map((signal, index) => (
                        <div key={signal.id || index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className="font-semibold">{signal.symbol}</div>
                            <Badge variant="outline">{signal.strategy}</Badge>
                            <div className="text-sm text-gray-500">
                              {((signal.confidence || 0) * 100).toFixed(0)}% confidence
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <div className="text-sm text-gray-500">Entry</div>
                              <div className="font-medium">{formatCurrency(signal.entry_price)}</div>
                            </div>
                            <div className="text-right">
                              <div className="text-sm text-gray-500">Target</div>
                              <div className="font-medium text-green-600">{formatCurrency(signal.target_price)}</div>
                            </div>
                            <Badge className={getStatusColor(signal.status || 'active')}>
                              {getStatusIcon(signal.status || 'active')}
                              <span className="ml-1 capitalize">{(signal.status || 'active').replace('_', ' ')}</span>
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Performance Tab */}
            <TabsContent value="performance" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Strategy Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {byStrategy.length === 0 ? (
                    <div className="text-center py-8">
                      <BarChart3 className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                      <p className="text-gray-500">No performance data available</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {byStrategy.map((strategy) => (
                        <div key={strategy.strategy} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-semibold capitalize">{strategy.strategy}</h4>
                            <Badge variant="outline">{strategy.total} signals</Badge>
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500">Success Rate:</span>
                              <div className="font-medium text-purple-600">{strategy.success_rate.toFixed(1)}%</div>
                            </div>
                            <div>
                              <span className="text-gray-500">Target Hits:</span>
                              <div className="font-medium text-green-600">{strategy.target_hits}</div>
                            </div>
                            <div>
                              <span className="text-gray-500">Stop Losses:</span>
                              <div className="font-medium text-red-600">{strategy.stop_losses}</div>
                            </div>
                            <div>
                              <span className="text-gray-500">Avg Profit:</span>
                              <div className="font-medium text-green-600">
                                {formatPercent(strategy.avg_profit_percent || 0)}
                              </div>
                            </div>
                          </div>
                          
                          <div className="mt-3">
                            <Progress value={strategy.success_rate} className="h-2" />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Generate Signals Dialog */}
          <Dialog open={showDialog} onOpenChange={setShowDialog}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Generate New Signals</DialogTitle>
                <DialogDescription>
                  Configure parameters for signal generation
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="strategy">Strategy</Label>
                  <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="multibagger">Multibagger</SelectItem>
                      <SelectItem value="momentum">Momentum</SelectItem>
                      <SelectItem value="breakout">Breakout</SelectItem>
                      <SelectItem value="value">Value</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="confidence">Minimum Confidence</Label>
                  <Input
                    id="confidence"
                    type="number"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={minConfidence}
                    onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
                  />
                </div>
              </div>
              
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={generateSignals} disabled={generating}>
                  {generating ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Target className="h-4 w-4 mr-2" />
                      Generate
                    </>
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </MainLayout>
    </ProtectedRoute>
  )
}
