'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Switch } from '@/components/ui/switch'
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  BarChart3, 
  RefreshCw, 
  DollarSign, 
  Users,
  Database,
  Target,
  AlertCircle,
  CheckCircle,
  Clock,
  Mail
} from 'lucide-react'

export default function EnhancedDashboard() {
  // State management
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // Data states
  const [apiStatus, setApiStatus] = useState(null)
  const [stocks, setStocks] = useState([])
  const [shariahStocks, setShariahStocks] = useState([])
  const [todaySignals, setTodaySignals] = useState([])
  const [openSignals, setOpenSignals] = useState([])
  const [signalTracking, setSignalTracking] = useState({})
  const [performance, setPerformance] = useState(null)
  const [backtestResults, setBacktestResults] = useState(null)
  
  // Settings
  const [shariahOnly, setShariahOnly] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(30000) // 30 seconds

  // API call wrapper with error handling
  const apiCall = useCallback(async (endpoint, options = {}) => {
    try {
      const response = await fetch(`/api${endpoint}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options
      })
      const data = await response.json()
      
      if (!data.success) {
        throw new Error(data.error || 'API call failed')
      }
      
      return data
    } catch (err) {
      console.error(`API Error (${endpoint}):`, err)
      setError(`${endpoint}: ${err.message}`)
      throw err
    }
  }, [])

  // 1. Check API Status
  const checkApiStatus = useCallback(async () => {
    try {
      const data = await apiCall('/')
      setApiStatus(data)
    } catch (err) {
      console.error('API status check failed:', err)
    }
  }, [apiCall])

  // 2. Load Stock Data
  const loadStocks = useCallback(async (shariah = false) => {
    try {
      const endpoint = shariah ? '/stocks/shariah' : '/stocks/all'
      const data = await apiCall(endpoint)
      
      if (shariah) {
        setShariahStocks(data.data.stocks || [])
      } else {
        setStocks(data.data.stocks || [])
      }
    } catch (err) {
      console.error('Failed to load stocks:', err)
    }
  }, [apiCall])

  // 3. Refresh Stock Prices
  const refreshStockPrices = useCallback(async () => {
    try {
      setLoading(true)
      await apiCall('/stocks/refresh', { method: 'POST' })
      
      // Reload stock data after refresh
      await loadStocks(false)
      await loadStocks(true)
      
      setError(null)
    } catch (err) {
      console.error('Failed to refresh stock prices:', err)
    } finally {
      setLoading(false)
    }
  }, [apiCall, loadStocks])

  // 4. Load Today's Signals
  const loadTodaySignals = useCallback(async () => {
    try {
      const data = await apiCall('/signals/today')
      setTodaySignals(data.data.signals || [])
    } catch (err) {
      console.error('Failed to load today signals:', err)
    }
  }, [apiCall])

  // 5. Load Open Signals
  const loadOpenSignals = useCallback(async () => {
    try {
      const data = await apiCall('/signals/open')
      setOpenSignals(data.data.signals || [])
      
      // Auto-track open signals
      if (data.data.signals && data.data.signals.length > 0) {
        const signalIds = data.data.signals.map(s => s.signal_id)
        await trackSignals(signalIds)
      }
    } catch (err) {
      console.error('Failed to load open signals:', err)
    }
  }, [apiCall])

  // 6. Generate New Signals
  const generateSignals = useCallback(async (strategy = 'momentum') => {
    try {
      setLoading(true)
      const data = await apiCall('/signals/generate', {
        method: 'POST',
        body: JSON.stringify({
          strategy,
          shariah_only: shariahOnly,
          min_confidence: 0.6
        })
      })
      
      setTodaySignals(data.data.signals || [])
      
      // Auto-track new signals
      if (data.data.signals && data.data.signals.length > 0) {
        const signalIds = data.data.signals.map(s => s.signal_id)
        await trackSignals(signalIds)
      }
      
      setError(null)
    } catch (err) {
      console.error('Failed to generate signals:', err)
    } finally {
      setLoading(false)
    }
  }, [apiCall, shariahOnly])

  // 7. Track Signal Performance
  const trackSignals = useCallback(async (signalIds) => {
    try {
      const data = await apiCall('/signals/track', {
        method: 'POST',
        body: JSON.stringify({
          signal_ids: signalIds,
          update_prices: true
        })
      })
      
      // Convert array to object for easier lookup
      const trackingData = {}
      if (data.data.results) {
        data.data.results.forEach(result => {
          trackingData[result.signal_id] = result
        })
      }
      setSignalTracking(trackingData)
    } catch (err) {
      console.error('Failed to track signals:', err)
    }
  }, [apiCall])

  // 8. Load Performance Summary
  const loadPerformance = useCallback(async (period = '30d') => {
    try {
      const data = await apiCall(`/performance/summary?period=${period}`)
      setPerformance(data.data)
    } catch (err) {
      console.error('Failed to load performance:', err)
    }
  }, [apiCall])

  // 9. Run Backtest
  const runBacktest = useCallback(async (strategy = 'momentum') => {
    try {
      setLoading(true)
      const data = await apiCall('/backtest', {
        method: 'POST',
        body: JSON.stringify({
          strategy,
          start_date: '2020-01-01',
          end_date: '2024-12-31',
          shariah_only: shariahOnly,
          initial_capital: 100000
        })
      })
      
      setBacktestResults(data.data)
      setError(null)
    } catch (err) {
      console.error('Failed to run backtest:', err)
    } finally {
      setLoading(false)
    }
  }, [apiCall, shariahOnly])

  // 10. Send Report
  const sendReport = useCallback(async (type = 'daily') => {
    try {
      setLoading(true)
      await apiCall('/report/send', {
        method: 'POST',
        body: JSON.stringify({
          type,
          email: 'user@example.com',
          include_performance: true,
          include_signals: true
        })
      })
      
      alert('Report sent successfully!')
      setError(null)
    } catch (err) {
      console.error('Failed to send report:', err)
    } finally {
      setLoading(false)
    }
  }, [apiCall])

  // Initialize dashboard
  useEffect(() => {
    const initializeDashboard = async () => {
      setLoading(true)
      try {
        // Load all initial data
        await Promise.all([
          checkApiStatus(),
          loadStocks(false),
          loadStocks(true),
          loadTodaySignals(),
          loadOpenSignals(),
          loadPerformance()
        ])
      } catch (err) {
        console.error('Dashboard initialization failed:', err)
      } finally {
        setLoading(false)
      }
    }

    initializeDashboard()
  }, [checkApiStatus, loadStocks, loadTodaySignals, loadOpenSignals, loadPerformance])

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(async () => {
      try {
        await Promise.all([
          refreshStockPrices(),
          loadTodaySignals(),
          loadOpenSignals(),
          loadPerformance()
        ])
      } catch (err) {
        console.error('Auto-refresh failed:', err)
      }
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, refreshStockPrices, loadTodaySignals, loadOpenSignals, loadPerformance])

  // Render signal card with tracking data
  const renderSignalCard = (signal) => {
    const tracking = signalTracking[signal.signal_id]
    const hasTracking = tracking && tracking.current_return !== undefined

    return (
      <Card key={signal.signal_id} className="mb-4">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-lg">{signal.symbol}</CardTitle>
              <CardDescription>{signal.strategy} strategy</CardDescription>
            </div>
            <div className="flex gap-2">
              <Badge variant={signal.signal_type === 'BUY' ? 'default' : 'destructive'}>
                {signal.signal_type}
              </Badge>
              {signal.shariah_compliant && (
                <Badge variant="outline">Shariah</Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Entry Price</p>
              <p className="font-semibold">₹{signal.entry_price?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Target</p>
              <p className="font-semibold text-green-600">₹{signal.target_price?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Stop Loss</p>
              <p className="font-semibold text-red-600">₹{signal.stop_loss?.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Confidence</p>
              <p className="font-semibold">{(signal.confidence * 100).toFixed(1)}%</p>
            </div>
          </div>
          
          {hasTracking && (
            <div className="mt-4 p-3 bg-muted rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Current Return:</span>
                <span className={`font-semibold ${tracking.current_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {(tracking.current_return * 100).toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className="text-sm text-muted-foreground">Current Price:</span>
                <span className="font-semibold">₹{tracking.current_price?.toFixed(2)}</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-primary text-primary-foreground p-2 rounded-lg">
                <BarChart3 className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">EmergentTrader Enhanced</h1>
                <p className="text-muted-foreground">Complete AI-Powered Trading Platform</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* API Status Indicator */}
              <div className="flex items-center space-x-2">
                {apiStatus ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-500" />
                )}
                <span className="text-sm">API {apiStatus ? 'Online' : 'Offline'}</span>
              </div>
              
              {/* Auto-refresh toggle */}
              <div className="flex items-center space-x-2">
                <Switch checked={autoRefresh} onCheckedChange={setAutoRefresh} />
                <span className="text-sm">Auto-refresh</span>
              </div>
              
              {/* Shariah filter */}
              <div className="flex items-center space-x-2">
                <Switch checked={shariahOnly} onCheckedChange={setShariahOnly} />
                <span className="text-sm">Shariah Only</span>
              </div>
              
              {/* Action buttons */}
              <Button variant="outline" onClick={refreshStockPrices} disabled={loading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              
              <Button onClick={() => generateSignals('momentum')} disabled={loading}>
                <Activity className="h-4 w-4 mr-2" />
                Generate Signals
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 border-destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-destructive">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Main Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="stocks">Stocks</TabsTrigger>
            <TabsTrigger value="signals">Signals</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="backtest">Backtest</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Stocks</CardTitle>
                  <Database className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stocks.length}</div>
                  <p className="text-xs text-muted-foreground">
                    {shariahStocks.length} Shariah compliant
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Today's Signals</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{todaySignals.length}</div>
                  <p className="text-xs text-muted-foreground">
                    {todaySignals.filter(s => s.signal_type === 'BUY').length} BUY signals
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Open Positions</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{openSignals.length}</div>
                  <p className="text-xs text-muted-foreground">
                    Active trading positions
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Performance</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {performance?.win_rate ? `${performance.win_rate.toFixed(1)}%` : 'N/A'}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Win rate
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Signals Preview */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Signals</CardTitle>
                <CardDescription>Latest trading signals generated</CardDescription>
              </CardHeader>
              <CardContent>
                {todaySignals.length > 0 ? (
                  <div className="space-y-4">
                    {todaySignals.slice(0, 3).map(renderSignalCard)}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No signals generated today</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Stocks Tab */}
          <TabsContent value="stocks" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Stock Universe</h2>
              <div className="flex gap-2">
                <Button variant="outline" onClick={refreshStockPrices} disabled={loading}>
                  <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh Prices
                </Button>
              </div>
            </div>

            <Card>
              <CardContent className="p-6">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Symbol</th>
                        <th className="text-left p-2">Name</th>
                        <th className="text-left p-2">Sector</th>
                        <th className="text-right p-2">Price</th>
                        <th className="text-right p-2">Market Cap</th>
                        <th className="text-center p-2">Shariah</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(shariahOnly ? shariahStocks : stocks).map(stock => (
                        <tr key={stock.symbol} className="border-b hover:bg-muted/50">
                          <td className="p-2 font-medium">{stock.symbol}</td>
                          <td className="p-2">{stock.name}</td>
                          <td className="p-2">{stock.sector}</td>
                          <td className="p-2 text-right">₹{stock.current_price?.toFixed(2)}</td>
                          <td className="p-2 text-right">₹{stock.market_cap?.toLocaleString()}</td>
                          <td className="p-2 text-center">
                            {stock.shariah_compliant ? (
                              <CheckCircle className="h-4 w-4 text-green-500 mx-auto" />
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Signals Tab */}
          <TabsContent value="signals" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Today's Signals</h2>
              <Button onClick={() => generateSignals('momentum')} disabled={loading}>
                <Activity className="h-4 w-4 mr-2" />
                Generate New Signals
              </Button>
            </div>

            {todaySignals.length > 0 ? (
              <div className="grid gap-4">
                {todaySignals.map(renderSignalCard)}
              </div>
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-muted-foreground">No signals generated today</p>
                  <Button 
                    onClick={() => generateSignals('momentum')} 
                    className="mt-4"
                    disabled={loading}
                  >
                    Generate First Signal
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Active Positions Tab */}
          <TabsContent value="active" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Active Positions</h2>
              <Button onClick={loadOpenSignals} disabled={loading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh Tracking
              </Button>
            </div>

            {openSignals.length > 0 ? (
              <div className="grid gap-4">
                {openSignals.map(renderSignalCard)}
              </div>
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-muted-foreground">No active positions</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Backtest Tab */}
          <TabsContent value="backtest" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Strategy Backtesting</h2>
              <Button onClick={() => runBacktest('momentum')} disabled={loading}>
                <BarChart3 className="h-4 w-4 mr-2" />
                Run Backtest
              </Button>
            </div>

            {backtestResults ? (
              <div className="grid gap-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-sm text-muted-foreground">Total Return</p>
                      <p className="text-2xl font-bold text-green-600">
                        {(backtestResults.performance_metrics?.total_return * 100 || 0).toFixed(1)}%
                      </p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                      <p className="text-2xl font-bold">
                        {backtestResults.performance_metrics?.sharpe_ratio?.toFixed(2) || 'N/A'}
                      </p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-sm text-muted-foreground">Max Drawdown</p>
                      <p className="text-2xl font-bold text-red-600">
                        {(backtestResults.performance_metrics?.max_drawdown * 100 || 0).toFixed(1)}%
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-muted-foreground">No backtest results available</p>
                  <Button 
                    onClick={() => runBacktest('momentum')} 
                    className="mt-4"
                    disabled={loading}
                  >
                    Run First Backtest
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Performance Analytics</h2>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => loadPerformance('7d')}>
                  7D
                </Button>
                <Button variant="outline" onClick={() => loadPerformance('30d')}>
                  30D
                </Button>
                <Button variant="outline" onClick={() => loadPerformance('90d')}>
                  90D
                </Button>
                <Button onClick={() => sendReport('daily')} disabled={loading}>
                  <Mail className="h-4 w-4 mr-2" />
                  Send Report
                </Button>
              </div>
            </div>

            {performance ? (
              <div className="grid gap-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-sm text-muted-foreground">Total Signals</p>
                      <p className="text-2xl font-bold">{performance.total_signals || 0}</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-sm text-muted-foreground">Win Rate</p>
                      <p className="text-2xl font-bold text-green-600">
                        {performance.win_rate?.toFixed(1) || 0}%
                      </p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-sm text-muted-foreground">Avg Return</p>
                      <p className="text-2xl font-bold">
                        {performance.avg_return?.toFixed(2) || 0}%
                      </p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-sm text-muted-foreground">Active Signals</p>
                      <p className="text-2xl font-bold">{performance.active_signals || 0}</p>
                    </CardContent>
                  </Card>
                </div>

                {performance.best_performing_stock && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Top Performers</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Best Performing</p>
                          <p className="font-semibold text-green-600">
                            {performance.best_performing_stock}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Worst Performing</p>
                          <p className="font-semibold text-red-600">
                            {performance.worst_performing_stock}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-muted-foreground">No performance data available</p>
                  <Button 
                    onClick={() => loadPerformance('30d')} 
                    className="mt-4"
                    disabled={loading}
                  >
                    Load Performance Data
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
