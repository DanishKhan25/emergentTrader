'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Target, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Calendar,
  DollarSign
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useWebSocket } from '@/contexts/WebSocketContext'

export default function SignalTrackingDashboard() {
  const [activeSignals, setActiveSignals] = useState([])
  const [statistics, setStatistics] = useState({})
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  
  const { getAuthHeaders } = useAuth()
  const { isConnected, lastMessage } = useWebSocket()

  useEffect(() => {
    fetchData()
  }, [])

  // Listen for WebSocket updates
  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'signal_generated') {
        fetchData() // Refresh data when new signal is generated
      } else if (lastMessage.type === 'target_hit' || lastMessage.type === 'stop_loss_hit') {
        fetchData() // Refresh when targets/stops are hit
      }
    }
  }, [lastMessage])

  const fetchData = async () => {
    try {
      setLoading(true)
      
      // Fetch active signals and statistics
      const [signalsResponse, statsResponse] = await Promise.all([
        fetch('/api/signals/active', {
          headers: getAuthHeaders()
        }),
        fetch('/api/signals/statistics', {
          headers: getAuthHeaders()
        })
      ])

      if (signalsResponse.ok && statsResponse.ok) {
        const signalsData = await signalsResponse.json()
        const statsData = await statsResponse.json()
        
        if (signalsData.success) {
          setActiveSignals(signalsData.signals || [])
        }
        
        if (statsData.success) {
          setStatistics(statsData)
        }
      }
    } catch (error) {
      console.error('Error fetching signal data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchData()
    setRefreshing(false)
  }

  const clearAllSignals = async () => {
    try {
      const response = await fetch('/api/signals/clear', {
        method: 'POST',
        headers: getAuthHeaders()
      })

      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          setActiveSignals([])
          fetchData() // Refresh statistics
        }
      }
    } catch (error) {
      console.error('Error clearing signals:', error)
    }
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  const overall = statistics.overall || {}
  const byStrategy = statistics.by_strategy || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Signal Tracking</h2>
          <p className="text-gray-600 mt-1">Monitor active signals and performance</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>{isConnected ? 'Live' : 'Offline'}</span>
          </div>
          <Button onClick={handleRefresh} disabled={refreshing} variant="outline">
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button onClick={clearAllSignals} variant="destructive">
            Clear All
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
          <TabsTrigger value="active">Active Signals</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        {/* Active Signals Tab */}
        <TabsContent value="active" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Active Signals ({activeSignals.length})
              </CardTitle>
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
                            <Badge className={getStatusColor(signal.status)}>
                              {getStatusIcon(signal.status)}
                              <span className="ml-1 capitalize">{signal.status.replace('_', ' ')}</span>
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500">Entry Price:</span>
                              <div className="font-medium">{formatCurrency(signal.entry_price)}</div>
                            </div>
                            <div>
                              <span className="text-gray-500">Current Price:</span>
                              <div className="font-medium">{formatCurrency(signal.current_price)}</div>
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
                              <span className="text-sm text-gray-500">Unrealized P&L:</span>
                              <span className={`font-medium ${signal.unrealized_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatPercent(signal.unrealized_pnl_percent || 0)}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4 text-gray-400" />
                              <span className="text-sm text-gray-500">{signal.days_active} days active</span>
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
                                ((signal.current_price - signal.stop_loss) / 
                                (signal.target_price - signal.stop_loss)) * 100
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
    </div>
  )
}
