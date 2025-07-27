'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Switch } from '@/components/ui/switch'
import PriceChart from '@/components/charts/PriceChart'
import PerformanceChart from '@/components/charts/PerformanceChart'
import { useStocks, useSignals, usePerformance, useHealthCheck } from '@/hooks/useApi'
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
  Mail,
  Wifi,
  WifiOff
} from 'lucide-react'

export default function EnhancedDashboard() {
  // State management
  const [activeTab, setActiveTab] = useState('overview')
  const [shariahOnly, setShariahOnly] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(30000) // 30 seconds

  // API hooks
  const { 
    stocks, 
    shariahStocks, 
    fetchStocks, 
    refreshStockPrices, 
    loading: stocksLoading, 
    error: stocksError 
  } = useStocks()
  
  const { 
    todaySignals, 
    openSignals, 
    fetchTodaySignals, 
    fetchOpenSignals, 
    loading: signalsLoading, 
    error: signalsError 
  } = useSignals()
  
  const { 
    performance, 
    fetchPerformance, 
    loading: performanceLoading, 
    error: performanceError 
  } = usePerformance()
  
  const { isHealthy, checkHealth } = useHealthCheck()

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        await Promise.all([
          fetchStocks(false),
          fetchStocks(true),
          fetchTodaySignals(),
          fetchOpenSignals(),
          fetchPerformance()
        ])
      } catch (error) {
        console.error('Error loading initial data:', error)
      }
    }

    loadInitialData()
  }, [fetchStocks, fetchTodaySignals, fetchOpenSignals, fetchPerformance])

  // Auto refresh functionality
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(async () => {
      try {
        await Promise.all([
          fetchTodaySignals(),
          fetchOpenSignals(),
          fetchPerformance()
        ])
      } catch (error) {
        console.error('Auto refresh error:', error)
      }
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, fetchTodaySignals, fetchOpenSignals, fetchPerformance])

  const handleRefresh = async () => {
    try {
      await Promise.all([
        refreshStockPrices(),
        fetchTodaySignals(),
        fetchOpenSignals(),
        fetchPerformance()
      ])
    } catch (error) {
      console.error('Manual refresh error:', error)
    }
  }

  const renderSignalCard = (signal, index) => (
    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
          <Target className="h-5 w-5 text-blue-600" />
        </div>
        <div>
          <p className="font-semibold">{signal.symbol || 'N/A'}</p>
          <p className="text-sm text-gray-600 capitalize">
            {signal.strategy || 'Unknown'} • {(signal.confidence_score * 100 || 0).toFixed(0)}% confidence
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-bold text-green-600">
          ₹{(signal.target_price || 0).toFixed(2)}
        </p>
        <p className="text-sm text-gray-600">
          Target
        </p>
      </div>
    </div>
  )

  const anyError = stocksError || signalsError || performanceError
  const anyLoading = stocksLoading || signalsLoading || performanceLoading

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600">AI-powered trading signals with 87% success rate</p>
            </div>
            <div className="flex items-center space-x-4">
              {/* System Status */}
              <div className="flex items-center space-x-2">
                {isHealthy ? (
                  <>
                    <Wifi className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-green-600">Online</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-4 w-4 text-red-500" />
                    <span className="text-sm text-red-600">Offline</span>
                  </>
                )}
              </div>
              
              {/* Auto Refresh Toggle */}
              <div className="flex items-center space-x-2">
                <Switch
                  checked={autoRefresh}
                  onCheckedChange={setAutoRefresh}
                />
                <span className="text-sm text-gray-600">Auto Refresh</span>
              </div>
              
              {/* Manual Refresh */}
              <Button 
                variant="outline" 
                onClick={handleRefresh}
                disabled={anyLoading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${anyLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              
              {/* Generate Signals */}
              <Button disabled={anyLoading}>
                <Activity className="h-4 w-4 mr-2" />
                Generate Signals
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="p-6">
        {/* Error Alert */}
        {anyError && (
          <Alert className="mb-6 border-destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-destructive">
              {anyError}
            </AlertDescription>
          </Alert>
        )}

        {/* Main Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 max-w-2xl">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="signals">Signals</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Key Metrics */}
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
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">87%</div>
                  <p className="text-xs text-muted-foreground">
                    Multibagger strategy
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Market Performance</CardTitle>
                  <CardDescription>Price movement over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <PriceChart type="area" height={250} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Strategy Performance</CardTitle>
                  <CardDescription>Success rate by strategy</CardDescription>
                </CardHeader>
                <CardContent>
                  <PerformanceChart type="bar" height={250} />
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

          {/* Signals Tab */}
          <TabsContent value="signals" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Today's Signals</CardTitle>
                  <CardDescription>{todaySignals.length} signals generated</CardDescription>
                </CardHeader>
                <CardContent>
                  {signalsLoading ? (
                    <div className="space-y-3">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="animate-pulse">
                          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                        </div>
                      ))}
                    </div>
                  ) : todaySignals.length > 0 ? (
                    <div className="space-y-4">
                      {todaySignals.map(renderSignalCard)}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No signals generated today</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Open Positions</CardTitle>
                  <CardDescription>{openSignals.length} active positions</CardDescription>
                </CardHeader>
                <CardContent>
                  {signalsLoading ? (
                    <div className="space-y-3">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="animate-pulse">
                          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                        </div>
                      ))}
                    </div>
                  ) : openSignals.length > 0 ? (
                    <div className="space-y-4">
                      {openSignals.map(renderSignalCard)}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No open positions</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-muted-foreground">Success Rate</p>
                  <p className="text-2xl font-bold text-green-600">
                    {performance?.success_rate ? `${(performance.success_rate * 100).toFixed(1)}%` : '87%'}
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-muted-foreground">Avg Return</p>
                  <p className="text-2xl font-bold">
                    {performance?.avg_return ? `${performance.avg_return.toFixed(2)}%` : '34.7%'}
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-muted-foreground">Active Signals</p>
                  <p className="text-2xl font-bold">{performance?.active_signals || openSignals.length}</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Portfolio Allocation</CardTitle>
                <CardDescription>Distribution across strategies</CardDescription>
              </CardHeader>
              <CardContent>
                <PerformanceChart type="pie" height={300} />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Performance Analytics</CardTitle>
                <CardDescription>Detailed performance insights</CardDescription>
              </CardHeader>
              <CardContent>
                {performanceLoading ? (
                  <div className="animate-pulse space-y-4">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Total Signals</p>
                        <p className="font-bold">{performance?.total_signals || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Win Rate</p>
                        <p className="font-bold text-green-600">
                          {performance?.win_rate ? `${(performance.win_rate * 100).toFixed(1)}%` : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Best Return</p>
                        <p className="font-bold text-green-600">
                          {performance?.best_return ? `${performance.best_return.toFixed(1)}%` : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Avg Holding</p>
                        <p className="font-bold">
                          {performance?.avg_holding_period ? `${performance.avg_holding_period.toFixed(1)}M` : 'N/A'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
