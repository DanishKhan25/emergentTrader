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

  const loadSignalData = async () => {
    try {
      setLoading(true)
      
      // Load signals, active signals, and statistics in parallel
      const [signalsResponse, activeResponse, statsResponse] = await Promise.all([
        fetch('/api/signals', { headers: getAuthHeaders() }),
        fetch('/api/signals/active', { headers: getAuthHeaders() }),
        fetch('/api/signals/statistics', { headers: getAuthHeaders() })
      ])

      // Handle signals response
      if (signalsResponse.ok) {
        const signalsData = await signalsResponse.json()
        if (signalsData.success) {
          setSignals(signalsData.data?.signals || [])
          setMarketDataAvailable(true)
        } else {
          console.warn('Signals API not available, using fallback')
          setMarketDataAvailable(false)
        }
      } else {
        setMarketDataAvailable(false)
      }

      // Handle active signals response
      if (activeResponse.ok) {
        const activeData = await activeResponse.json()
        if (activeData.success) {
          setActiveSignals(activeData.signals || [])
        }
      }

      // Handle statistics response
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        if (statsData.success) {
          setSignalStats(statsData)
        }
      }

    } catch (error) {
      console.error('Error loading signal data:', error)
      setMarketDataAvailable(false)
      
      // Show user-friendly notification
      addNotification({
        type: 'warning',
        title: 'Market Data Service',
        message: 'Market data service not available, using cached data',
        duration: 5000
      })
    } finally {
      setLoading(false)
    }
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
    try {
      const response = await fetch('/api/signals/statistics', { 
        headers: getAuthHeaders() 
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setSignalStats(data)
        }
      }
    } catch (error) {
      console.error('Error loading signal statistics:', error)
    }
  }

  const generateSignals = async () => {
    try {
      setGenerating(true)
      
      const response = await fetch('/api/signals/generate', {
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
          message: result.error || 'Failed to generate signals',
          duration: 5000
        })
      }
    } catch (error) {
      console.error('Error generating signals:', error)
      addNotification({
        type: 'error',
        title: 'Generation Error',
        message: 'An error occurred while generating signals',
        duration: 5000
      })
    } finally {
      setGenerating(false)
    }
  }

  const clearAllSignals = async () => {
    try {
      const response = await fetch('/api/signals/clear', {
        method: 'POST',
        headers: getAuthHeaders()
      })

      const result = await response.json()
      
      if (result.success) {
        setSignals([])
        setActiveSignals([])
        setSignalStats({})
        
        addNotification({
          type: 'info',
          title: 'Signals Cleared',
          message: `Cleared ${result.count_cleared || 0} signals from database`,
          duration: 5000
        })
      }
    } catch (error) {
      console.error('Error clearing signals:', error)
      addNotification({
        type: 'error',
        title: 'Clear Failed',
        message: 'Failed to clear signals',
        duration: 5000
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
  AlertTriangle,
  CheckCircle,
  Activity,
  Zap,
  RefreshCw,
  ShoppingCart,
  Eye,
  Filter
} from 'lucide-react'

export default function SignalsPage() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showBuyModal, setShowBuyModal] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [selectedSignal, setSelectedSignal] = useState(null)
  const [buyData, setBuyData] = useState({
    quantity: '',
    entry_price: '',
    target_price: '',
    stop_loss: ''
  })
  const [actionLoading, setActionLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [selectedStrategy, setSelectedStrategy] = useState('momentum')

  const strategies = [
    { value: 'momentum', label: 'Momentum', icon: TrendingUp },
    { value: 'multibagger', label: 'Multibagger', icon: Target },
    { value: 'swing', label: 'Swing Trading', icon: Activity },
    { value: 'value_investing', label: 'Value Investing', icon: Shield },
    { value: 'breakout', label: 'Breakout', icon: Zap },
    { value: 'mean_reversion', label: 'Mean Reversion', icon: RefreshCw }
  ]

  useEffect(() => {
    fetchSignals()
  }, [])

  const fetchSignals = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('http://localhost:8000/signals/active')
      const result = await response.json()
      
      if (result.success) {
        setSignals(result.data.signals || [])
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const generateNewSignals = async (strategy = 'momentum') => {
    try {
      setGenerating(true)
      setError(null)
      
      const response = await fetch('http://localhost:8000/signals/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy: strategy,
          symbols: null,
          shariah_only: true,
          min_confidence: 0.6,
          enable_ml: true
        })
      })
      
      const result = await response.json()
      if (result.success) {
        alert(`Generated ${result.data.signals?.length || 0} new signals!`)
        fetchSignals() // Refresh the signals list
      } else {
        throw new Error(result.error)
      }
    } catch (err) {
      setError(`Error generating signals: ${err.message}`)
    } finally {
      setGenerating(false)
    }
  }

  const handleBuySignal = async () => {
    setActionLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/signals/${selectedSignal.id}/buy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...buyData,
          signal_data: selectedSignal
        })
      })
      
      const result = await response.json()
      if (result.success) {
        alert(`Successfully bought ${selectedSignal.symbol}!`)
        setShowBuyModal(false)
        setBuyData({ quantity: '', entry_price: '', target_price: '', stop_loss: '' })
      } else {
        throw new Error(result.error)
      }
    } catch (err) {
      alert(`Error buying signal: ${err.message}`)
    } finally {
      setActionLoading(false)
    }
  }

  const openBuyModal = (signal) => {
    setSelectedSignal(signal)
    const currentPrice = signal.entry_price || signal.price || 0
    setBuyData({
      quantity: '10',
      entry_price: currentPrice.toString(),
      target_price: signal.target_price?.toString() || (currentPrice * 1.2).toFixed(2),
      stop_loss: signal.stop_loss?.toString() || (currentPrice * 0.9).toFixed(2)
    })
    setShowBuyModal(true)
  }

  const handleViewSignal = (signal) => {
    setSelectedSignal(signal)
    setShowDetailsModal(true)
  }

  const getStrategyIcon = (strategy) => {
    switch (strategy?.toLowerCase()) {
      case 'multibagger': return <Target className="h-4 w-4" />
      case 'momentum': return <TrendingUp className="h-4 w-4" />
      case 'swing': return <Activity className="h-4 w-4" />
      case 'breakout': return <Zap className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.8) return <Badge className="bg-green-100 text-green-800">High</Badge>
    if (confidence >= 0.6) return <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>
    return <Badge className="bg-red-100 text-red-800">Low</Badge>
  }

  const formatCurrency = (value) => {
    if (typeof value !== 'number') return '₹0'
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const SignalCard = ({ signal }) => {
    const currentPrice = signal.entry_price || signal.price || 0
    const targetPrice = signal.target_price || 0
    const confidence = signal.confidence || signal.confidence_score || 0
    
    // Calculate upside safely
    const upside = currentPrice > 0 && targetPrice > 0 
      ? ((targetPrice - currentPrice) / currentPrice * 100).toFixed(1)
      : 'N/A'
    
    return (
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                {getStrategyIcon(signal.strategy)}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-lg">{signal.symbol}</h3>
                  <Badge variant="outline" className="text-xs">Signal</Badge>
                </div>
                <p className="text-sm text-gray-600 capitalize">{signal.strategy?.replace('_', ' ')}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {getConfidenceBadge(confidence)}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Entry Price</p>
              <p className="font-semibold">{formatCurrency(currentPrice)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Confidence</p>
              <p className="font-semibold">{(confidence * 100).toFixed(1)}%</p>
            </div>
          </div>

          {targetPrice > 0 && (
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Target</p>
                <p className="font-semibold text-green-600">{formatCurrency(targetPrice)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Upside</p>
                <p className="font-semibold text-green-600">
                  {upside !== 'N/A' ? `${upside}%` : 'N/A'}
                </p>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="h-4 w-4 mr-1" />
              {new Date(signal.generated_at || signal.timestamp).toLocaleDateString()}
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={() => handleViewSignal(signal)}>
                <Eye className="h-4 w-4 mr-1" />
                View
              </Button>
              <Button size="sm" onClick={() => openBuyModal(signal)}>
                <ShoppingCart className="h-4 w-4 mr-1" />
                Buy
              </Button>
            </div>
          </div>

          {signal.sector && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-sm text-gray-600">
                <strong>Sector:</strong> {signal.sector}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="p-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Trading Signals</h1>
            <p className="text-gray-600 mt-2">
              AI-generated trading opportunities. Click "Buy" to convert signals to positions.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select strategy" />
              </SelectTrigger>
              <SelectContent>
                {strategies.map((strategy) => (
                  <SelectItem key={strategy.value} value={strategy.value}>
                    <div className="flex items-center space-x-2">
                      <strategy.icon className="h-4 w-4" />
                      <span>{strategy.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Button 
              onClick={() => generateNewSignals(selectedStrategy)}
              disabled={generating}
            >
              {generating ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Zap className="h-4 w-4 mr-2" />
              )}
              Generate Signals
            </Button>
            
            <Button variant="outline" onClick={fetchSignals} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Signals Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Signals</p>
                  <p className="text-2xl font-bold">{signals.length}</p>
                </div>
                <Activity className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">High Confidence</p>
                  <p className="text-2xl font-bold text-green-600">
                    {signals.filter(s => (s.confidence || s.confidence_score || 0) >= 0.8).length}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Momentum</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {signals.filter(s => s.strategy === 'momentum').length}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Multibagger</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {signals.filter(s => s.strategy === 'multibagger').length}
                  </p>
                </div>
                <Target className="h-8 w-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Signals Grid */}
        {error ? (
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Signals</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={fetchSignals}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        ) : signals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {signals.map((signal, index) => (
              <SignalCard key={signal.id || index} signal={signal} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Signals Available</h2>
            <p className="text-gray-600 mb-6">
              No trading signals found. Generate new signals to get AI-powered trading recommendations.
            </p>
            
            <div className="flex justify-center items-center space-x-4 mb-4">
              <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select strategy" />
                </SelectTrigger>
                <SelectContent>
                  {strategies.map((strategy) => (
                    <SelectItem key={strategy.value} value={strategy.value}>
                      <div className="flex items-center space-x-2">
                        <strategy.icon className="h-4 w-4" />
                        <span>{strategy.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Button 
                onClick={() => generateNewSignals(selectedStrategy)}
                disabled={generating}
                size="lg"
              >
                {generating ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Zap className="h-4 w-4 mr-2" />
                )}
                Generate {strategies.find(s => s.value === selectedStrategy)?.label} Signals
              </Button>
            </div>
          </div>
        )}

        {/* Buy Signal Modal */}
        <Dialog open={showBuyModal} onOpenChange={setShowBuyModal}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Buy Signal: {selectedSignal?.symbol}</DialogTitle>
              <DialogDescription>
                Convert this signal to an actual position in your portfolio
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    type="number"
                    value={buyData.quantity}
                    onChange={(e) => setBuyData(prev => ({ ...prev, quantity: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="entry_price">Entry Price</Label>
                  <Input
                    id="entry_price"
                    type="number"
                    step="0.01"
                    value={buyData.entry_price}
                    onChange={(e) => setBuyData(prev => ({ ...prev, entry_price: e.target.value }))}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="target_price">Target Price (Optional)</Label>
                  <Input
                    id="target_price"
                    type="number"
                    step="0.01"
                    value={buyData.target_price}
                    onChange={(e) => setBuyData(prev => ({ ...prev, target_price: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="stop_loss">Stop Loss (Optional)</Label>
                  <Input
                    id="stop_loss"
                    type="number"
                    step="0.01"
                    value={buyData.stop_loss}
                    onChange={(e) => setBuyData(prev => ({ ...prev, stop_loss: e.target.value }))}
                  />
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-md">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Investment Required:</span>
                  <span className="font-bold text-blue-600">
                    {formatCurrency((parseFloat(buyData.quantity) || 0) * (parseFloat(buyData.entry_price) || 0))}
                  </span>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowBuyModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleBuySignal} disabled={actionLoading}>
                {actionLoading ? 'Buying...' : 'Buy Signal'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        {/* Signal Details Modal */}
        <Dialog open={showDetailsModal} onOpenChange={setShowDetailsModal}>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                {selectedSignal && getStrategyIcon(selectedSignal.strategy)}
                <span>{selectedSignal?.symbol} - Signal Details</span>
              </DialogTitle>
              <DialogDescription>
                Detailed analysis and information about this trading signal
              </DialogDescription>
            </DialogHeader>

            {selectedSignal && (
              <div className="space-y-6">
                {/* Basic Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Symbol</Label>
                      <p className="text-lg font-semibold">{selectedSignal.symbol}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Strategy</Label>
                      <p className="capitalize">{selectedSignal.strategy?.replace('_', ' ')}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Sector</Label>
                      <p>{selectedSignal.sector || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Confidence</Label>
                      <div className="flex items-center space-x-2">
                        <p className="text-lg font-semibold">
                          {((selectedSignal.confidence || selectedSignal.confidence_score || 0) * 100).toFixed(1)}%
                        </p>
                        {getConfidenceBadge(selectedSignal.confidence || selectedSignal.confidence_score || 0)}
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Generated</Label>
                      <p>{new Date(selectedSignal.generated_at || selectedSignal.timestamp).toLocaleString()}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Signal Type</Label>
                      <Badge variant="outline" className="bg-green-50 text-green-700">
                        {selectedSignal.signal_type || 'BUY'}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Price Info */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-3">Price Analysis</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label className="text-sm text-gray-600">Entry Price</Label>
                      <p className="text-lg font-semibold text-blue-600">
                        {formatCurrency(selectedSignal.entry_price || 0)}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm text-gray-600">Target Price</Label>
                      <p className="text-lg font-semibold text-green-600">
                        {formatCurrency(selectedSignal.target_price || 0)}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm text-gray-600">Stop Loss</Label>
                      <p className="text-lg font-semibold text-red-600">
                        {formatCurrency(selectedSignal.stop_loss || 0)}
                      </p>
                    </div>
                  </div>
                  
                  {selectedSignal.entry_price && selectedSignal.target_price && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Potential Upside:</span>
                        <span className="font-semibold text-green-600">
                          {(((selectedSignal.target_price - selectedSignal.entry_price) / selectedSignal.entry_price) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Risk/Reward Ratio:</span>
                        <span className="font-semibold">
                          {selectedSignal.risk_reward_ratio || 'N/A'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Technical Indicators */}
                {(selectedSignal.rsi || selectedSignal.momentum_score || selectedSignal.volume_ratio) && (
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-3">Technical Indicators</h4>
                    <div className="grid grid-cols-3 gap-4">
                      {selectedSignal.rsi && (
                        <div>
                          <Label className="text-sm text-gray-600">RSI</Label>
                          <p className="font-semibold">{selectedSignal.rsi.toFixed(2)}</p>
                        </div>
                      )}
                      {selectedSignal.momentum_score && (
                        <div>
                          <Label className="text-sm text-gray-600">Momentum Score</Label>
                          <p className="font-semibold">{selectedSignal.momentum_score.toFixed(2)}</p>
                        </div>
                      )}
                      {selectedSignal.volume_ratio && (
                        <div>
                          <Label className="text-sm text-gray-600">Volume Ratio</Label>
                          <p className="font-semibold">{selectedSignal.volume_ratio.toFixed(2)}x</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Additional Info */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <Label className="text-gray-600">Market Cap</Label>
                    <p>{selectedSignal.market_cap ? `₹${(selectedSignal.market_cap / 10000000).toFixed(0)} Cr` : 'N/A'}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Shariah Compliant</Label>
                    <p>{selectedSignal.shariah_compliant ? '✅ Yes' : '❌ No'}</p>
                  </div>
                </div>
              </div>
            )}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowDetailsModal(false)}>
                Close
              </Button>
              <Button onClick={() => {
                setShowDetailsModal(false)
                openBuyModal(selectedSignal)
              }}>
                <ShoppingCart className="h-4 w-4 mr-2" />
                Buy This Signal
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  )
}
