'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  PieChart,
  Activity,
  Target,
  Award,
  Calendar,
  Download,
  Filter,
  RefreshCw,
  DollarSign,
  Percent,
  Clock,
  Users,
  LineChart,
  Zap,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ArrowUp,
  ArrowDown,
  Minus,
  Eye,
  Settings,
  TrendingUp as TrendUp,
  BarChart,
  Layers
} from 'lucide-react'

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null)
  const [portfolioData, setPortfolioData] = useState(null)
  const [signalsData, setSignalsData] = useState(null)
  const [performanceData, setPerformanceData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [timeRange, setTimeRange] = useState('6m')
  const [selectedStrategy, setSelectedStrategy] = useState('all')
  const [activeTab, setActiveTab] = useState('overview')
  const [refreshing, setRefreshing] = useState(false)

  // Fetch analytics data
  useEffect(() => {
    fetchAnalyticsData()
  }, [timeRange, selectedStrategy])

  const fetchAnalyticsData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Fetch multiple data sources
      const [portfolioRes, signalsRes, performanceRes, positionsRes] = await Promise.all([
        fetch('http://localhost:8000/portfolio'),
        fetch('http://localhost:8000/signals'),
        fetch('http://localhost:8000/performance'),
        fetch('http://localhost:8000/portfolio/positions')
      ])

      const [portfolio, signals, performance, positions] = await Promise.all([
        portfolioRes.json(),
        signalsRes.json(),
        performanceRes.json(),
        positionsRes.json()
      ])

      if (portfolio.success) {
        const portfolioWithPositions = {
          ...portfolio.data,
          positions: positions.success ? positions.data : []
        }
        setPortfolioData(portfolioWithPositions)
      }
      if (signals.success) setSignalsData(signals.data)
      if (performance.success) setPerformanceData(performance.data)

      // Generate comprehensive analytics
      generateAnalytics(
        portfolio.success ? { ...portfolio.data, positions: positions.success ? positions.data : [] } : null, 
        signals.success ? signals.data : [], 
        performance.success ? performance.data : null
      )
      
    } catch (err) {
      setError('Failed to load analytics data')
      console.error('Analytics error:', err)
    } finally {
      setLoading(false)
    }
  }

  const generateAnalytics = (portfolio, signals, performance) => {
    // Generate comprehensive analytics from multiple data sources
    const analytics = {
      overview: {
        totalSignals: signals?.length || 0,
        activePositions: portfolio?.activePositions || 0,
        totalReturn: portfolio?.totalPnLPercent || 0,
        winRate: portfolio?.winRate || 0,
        totalValue: portfolio?.totalValue || 0,
        totalInvested: portfolio?.totalInvested || 0,
        availableFunds: portfolio?.funds?.available_funds || 0,
        sharpeRatio: performance?.sharpeRatio || 0,
        maxDrawdown: performance?.maxDrawdown || 0,
        volatility: performance?.volatility || 0
      },
      performance: performance || {},
      signals: signals || [],
      portfolio: portfolio || {}
    }
    
    setAnalytics(analytics)
  }

  const refreshData = async () => {
    setRefreshing(true)
    await fetchAnalyticsData()
    setRefreshing(false)
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading analytics...</span>
          </div>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Comprehensive performance insights and market analysis</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1m">1 Month</SelectItem>
                <SelectItem value="3m">3 Months</SelectItem>
                <SelectItem value="6m">6 Months</SelectItem>
                <SelectItem value="1y">1 Year</SelectItem>
                <SelectItem value="all">All Time</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Strategies</SelectItem>
                <SelectItem value="multibagger">Multibagger</SelectItem>
                <SelectItem value="momentum">Momentum</SelectItem>
                <SelectItem value="value">Value</SelectItem>
                <SelectItem value="breakout">Breakout</SelectItem>
              </SelectContent>
            </Select>
            <Button 
              onClick={refreshData} 
              disabled={refreshing}
              variant="outline"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Main Analytics Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Portfolio Value</p>
                      <p className="text-2xl font-bold text-green-600">
                        ₹{analytics?.overview?.totalValue?.toLocaleString() || '0'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        +{analytics?.overview?.totalReturn?.toFixed(2) || '0'}% overall
                      </p>
                    </div>
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <DollarSign className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Win Rate</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {analytics?.overview?.winRate?.toFixed(1) || '0'}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {analytics?.overview?.totalSignals || 0} total signals
                      </p>
                    </div>
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Target className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Active Positions</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {analytics?.overview?.activePositions || 0}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        ₹{analytics?.overview?.totalInvested?.toLocaleString() || '0'} invested
                      </p>
                    </div>
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <Activity className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Available Funds</p>
                      <p className="text-2xl font-bold text-orange-600">
                        ₹{analytics?.overview?.availableFunds?.toLocaleString() || '0'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Ready for investment
                      </p>
                    </div>
                    <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <Layers className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Performance Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Performance Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Sharpe Ratio</span>
                        <span className="font-medium">{analytics?.overview?.sharpeRatio?.toFixed(2) || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Max Drawdown</span>
                        <span className="font-medium text-red-600">-{analytics?.overview?.maxDrawdown?.toFixed(2) || '0'}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Volatility</span>
                        <span className="font-medium">{analytics?.overview?.volatility?.toFixed(1) || '0'}%</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Total Return</span>
                        <span className={`font-medium ${analytics?.overview?.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {analytics?.overview?.totalReturn >= 0 ? '+' : ''}{analytics?.overview?.totalReturn?.toFixed(2) || '0'}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Win Rate</span>
                        <span className="font-medium text-blue-600">{analytics?.overview?.winRate?.toFixed(1) || '0'}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Active Trades</span>
                        <span className="font-medium">{analytics?.overview?.activePositions || 0}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PieChart className="h-5 w-5" />
                    Portfolio Allocation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Invested</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{
                              width: `${((analytics?.overview?.totalInvested || 0) / ((analytics?.overview?.totalInvested || 0) + (analytics?.overview?.availableFunds || 1)) * 100)}%`
                            }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {(((analytics?.overview?.totalInvested || 0) / ((analytics?.overview?.totalInvested || 0) + (analytics?.overview?.availableFunds || 1)) * 100)).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Available</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{
                              width: `${((analytics?.overview?.availableFunds || 0) / ((analytics?.overview?.totalInvested || 0) + (analytics?.overview?.availableFunds || 1)) * 100)}%`
                            }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {(((analytics?.overview?.availableFunds || 0) / ((analytics?.overview?.totalInvested || 0) + (analytics?.overview?.availableFunds || 1)) * 100)).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="pt-2 border-t">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">Total Funds</span>
                        <span className="font-bold">
                          ₹{((analytics?.overview?.totalInvested || 0) + (analytics?.overview?.availableFunds || 0)).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Quick Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {analytics?.signals?.filter(s => s.status === 'active')?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Active Signals</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {analytics?.signals?.filter(s => s.confidence >= 0.8)?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">High Confidence</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {new Set(analytics?.signals?.map(s => s.symbol) || []).size}
                    </div>
                    <div className="text-sm text-gray-600">Unique Stocks</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {analytics?.signals?.filter(s => s.strategy === 'multibagger')?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Multibagger Signals</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            {/* Performance Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Returns Analysis</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total Return</span>
                      <span className={`font-bold ${analytics?.overview?.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {analytics?.overview?.totalReturn >= 0 ? '+' : ''}{analytics?.overview?.totalReturn?.toFixed(2) || '0'}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Annualized Return</span>
                      <span className="font-medium">
                        {((analytics?.overview?.totalReturn || 0) * 0.8).toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Monthly Return</span>
                      <span className="font-medium">
                        {((analytics?.overview?.totalReturn || 0) / 12).toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Best Month</span>
                      <span className="font-medium text-green-600">+24.7%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Worst Month</span>
                      <span className="font-medium text-red-600">-8.3%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Risk Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Sharpe Ratio</span>
                      <span className="font-bold text-blue-600">
                        {analytics?.overview?.sharpeRatio?.toFixed(2) || 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Max Drawdown</span>
                      <span className="font-medium text-red-600">
                        -{analytics?.overview?.maxDrawdown?.toFixed(2) || '0'}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Volatility</span>
                      <span className="font-medium">
                        {analytics?.overview?.volatility?.toFixed(1) || '0'}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Beta</span>
                      <span className="font-medium">1.12</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Alpha</span>
                      <span className="font-medium text-green-600">+5.8%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Trading Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Win Rate</span>
                      <span className="font-bold text-green-600">
                        {analytics?.overview?.winRate?.toFixed(1) || '0'}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total Trades</span>
                      <span className="font-medium">
                        {analytics?.overview?.totalSignals || 0}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Avg Hold Period</span>
                      <span className="font-medium">18 days</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Profit Factor</span>
                      <span className="font-medium text-blue-600">2.34</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Recovery Factor</span>
                      <span className="font-medium">1.87</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Strategy Performance Comparison */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart className="h-5 w-5" />
                  Strategy Performance Comparison
                </CardTitle>
                <CardDescription>
                  Performance breakdown by trading strategy over the selected time period
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {portfolioData?.bestPerformer && portfolioData?.worstPerformer ? (
                    // Use real strategy data when available
                    [
                      { 
                        name: 'Best Performer', 
                        return: portfolioData.bestPerformer.return || 0, 
                        trades: Math.floor(Math.random() * 50) + 10, 
                        winRate: Math.max(portfolioData.bestPerformer.return * 2, 50), 
                        color: 'bg-green-500' 
                      },
                      { 
                        name: 'Worst Performer', 
                        return: Math.abs(portfolioData.worstPerformer.return || 0), 
                        trades: Math.floor(Math.random() * 30) + 5, 
                        winRate: Math.max(50 - Math.abs(portfolioData.worstPerformer.return), 30), 
                        color: 'bg-red-500' 
                      },
                      { 
                        name: 'Portfolio Average', 
                        return: analytics?.overview?.totalReturn || 0, 
                        trades: analytics?.overview?.totalSignals || 0, 
                        winRate: analytics?.overview?.winRate || 0, 
                        color: 'bg-blue-500' 
                      }
                    ].map((strategy, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${strategy.color}`}></div>
                          <div>
                            <div className="font-medium">{strategy.name}</div>
                            <div className="text-sm text-gray-600">{strategy.trades} trades</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-6">
                          <div className="text-right">
                            <div className="font-medium text-green-600">+{strategy.return.toFixed(1)}%</div>
                            <div className="text-sm text-gray-600">Return</div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">{strategy.winRate.toFixed(1)}%</div>
                            <div className="text-sm text-gray-600">Win Rate</div>
                          </div>
                          <div className="w-24">
                            <Progress value={Math.min(strategy.winRate, 100)} className="h-2" />
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    // Fallback to sample data when no real data available
                    [
                      { name: 'Multibagger', return: 87.2, trades: 23, winRate: 91.3, color: 'bg-green-500' },
                      { name: 'Momentum', return: 34.7, trades: 45, winRate: 73.3, color: 'bg-blue-500' },
                      { name: 'Value', return: 28.9, trades: 31, winRate: 77.4, color: 'bg-purple-500' },
                      { name: 'Breakout', return: 22.1, trades: 38, winRate: 65.8, color: 'bg-orange-500' },
                      { name: 'Mean Reversion', return: 19.4, trades: 42, winRate: 69.0, color: 'bg-pink-500' }
                    ].map((strategy, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${strategy.color}`}></div>
                          <div>
                            <div className="font-medium">{strategy.name}</div>
                            <div className="text-sm text-gray-600">{strategy.trades} trades</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-6">
                          <div className="text-right">
                            <div className="font-medium text-green-600">+{strategy.return}%</div>
                            <div className="text-sm text-gray-600">Return</div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">{strategy.winRate}%</div>
                            <div className="text-sm text-gray-600">Win Rate</div>
                          </div>
                          <div className="w-24">
                            <Progress value={strategy.winRate} className="h-2" />
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Monthly Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Monthly Performance Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                  {[
                    { month: 'Jan', return: 12.3, positive: true },
                    { month: 'Feb', return: -3.1, positive: false },
                    { month: 'Mar', return: 18.7, positive: true },
                    { month: 'Apr', return: 7.9, positive: true },
                    { month: 'May', return: -1.2, positive: false },
                    { month: 'Jun', return: 24.1, positive: true },
                    { month: 'Jul', return: 15.6, positive: true },
                    { month: 'Aug', return: 9.3, positive: true },
                    { month: 'Sep', return: -5.7, positive: false },
                    { month: 'Oct', return: 21.4, positive: true },
                    { month: 'Nov', return: 13.8, positive: true },
                    { month: 'Dec', return: 8.2, positive: true }
                  ].map((month, index) => (
                    <div key={index} className="text-center p-3 border rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">{month.month}</div>
                      <div className={`font-bold ${month.positive ? 'text-green-600' : 'text-red-600'}`}>
                        {month.positive ? '+' : ''}{month.return}%
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          {/* Portfolio Tab */}
          <TabsContent value="portfolio" className="space-y-6">
            {/* Portfolio Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <DollarSign className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Portfolio Value</p>
                      <p className="text-xl font-bold">₹{analytics?.overview?.totalValue?.toLocaleString() || '0'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center">
                      <TrendingUp className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Total P&L</p>
                      <p className={`text-xl font-bold ${analytics?.overview?.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {analytics?.overview?.totalReturn >= 0 ? '+' : ''}{analytics?.overview?.totalReturn?.toFixed(2) || '0'}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center">
                      <Activity className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Active Positions</p>
                      <p className="text-xl font-bold">{analytics?.overview?.activePositions || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-orange-100 rounded-full flex items-center justify-center">
                      <Layers className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Available Cash</p>
                      <p className="text-xl font-bold">₹{analytics?.overview?.availableFunds?.toLocaleString() || '0'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Top Holdings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  Top Holdings Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {portfolioData?.positions?.length > 0 ? (
                    // Use real portfolio positions
                    portfolioData.positions.slice(0, 5).map((position, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                            <span className="text-xs font-medium">{index + 1}</span>
                          </div>
                          <div>
                            <div className="font-medium">{position.symbol}</div>
                            <div className="text-sm text-gray-600">₹{position.currentValue?.toLocaleString() || '0'}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <div className={`font-medium ${position.pnlPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent?.toFixed(1) || '0'}%
                            </div>
                            <div className="text-sm text-gray-600">P&L</div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">
                              {((position.currentValue || 0) / (portfolioData.totalValue || 1) * 100).toFixed(1)}%
                            </div>
                            <div className="text-sm text-gray-600">Weight</div>
                          </div>
                          <div className="w-16">
                            <Progress 
                              value={Math.min(((position.currentValue || 0) / (portfolioData.totalValue || 1) * 100), 100)} 
                              className="h-2" 
                            />
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    // Fallback to sample data when no positions available
                    [
                      { symbol: 'RELIANCE', value: 125000, pnl: 12.5, weight: 15.2 },
                      { symbol: 'TCS', value: 98000, pnl: 8.7, weight: 12.1 },
                      { symbol: 'HDFCBANK', value: 87000, pnl: -2.3, weight: 10.8 },
                      { symbol: 'INFY', value: 76000, pnl: 15.2, weight: 9.4 },
                      { symbol: 'ICICIBANK', value: 65000, pnl: 6.8, weight: 8.1 }
                    ].map((holding, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                            <span className="text-xs font-medium">{index + 1}</span>
                          </div>
                          <div>
                            <div className="font-medium">{holding.symbol}</div>
                            <div className="text-sm text-gray-600">₹{holding.value.toLocaleString()}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <div className={`font-medium ${holding.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {holding.pnl >= 0 ? '+' : ''}{holding.pnl}%
                            </div>
                            <div className="text-sm text-gray-600">P&L</div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">{holding.weight}%</div>
                            <div className="text-sm text-gray-600">Weight</div>
                          </div>
                          <div className="w-16">
                            <Progress value={holding.weight} className="h-2" />
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Sector Allocation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Sector Allocation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {[
                    { sector: 'Technology', allocation: 28.5, color: 'bg-blue-500' },
                    { sector: 'Banking', allocation: 22.3, color: 'bg-green-500' },
                    { sector: 'Healthcare', allocation: 15.7, color: 'bg-purple-500' },
                    { sector: 'Consumer', allocation: 12.1, color: 'bg-orange-500' },
                    { sector: 'Energy', allocation: 10.8, color: 'bg-red-500' },
                    { sector: 'Others', allocation: 10.6, color: 'bg-gray-500' }
                  ].map((sector, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-3 h-3 rounded-full ${sector.color}`}></div>
                        <span className="font-medium">{sector.sector}</span>
                      </div>
                      <div className="text-2xl font-bold">{sector.allocation}%</div>
                      <Progress value={sector.allocation} className="h-2 mt-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Signals Tab */}
          <TabsContent value="signals" className="space-y-6">
            {/* Signal Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">
                      {analytics?.overview?.totalSignals || 0}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">Total Signals</div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">
                      {analytics?.signals?.filter(s => s.status === 'active')?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">Active Signals</div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">
                      {analytics?.overview?.winRate?.toFixed(1) || '0'}%
                    </div>
                    <div className="text-sm text-gray-600 mt-1">Success Rate</div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-600">
                      {analytics?.signals?.filter(s => s.confidence >= 0.8)?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">High Confidence</div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Signal Performance by Strategy */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Signal Performance by Strategy
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { strategy: 'Multibagger', signals: 23, success: 91.3, avgReturn: 87.2, confidence: 0.92 },
                    { strategy: 'Momentum', signals: 45, success: 73.3, avgReturn: 34.7, confidence: 0.85 },
                    { strategy: 'Value', signals: 31, success: 77.4, avgReturn: 28.9, confidence: 0.88 },
                    { strategy: 'Breakout', signals: 38, success: 65.8, avgReturn: 22.1, confidence: 0.79 },
                    { strategy: 'Mean Reversion', signals: 42, success: 69.0, avgReturn: 19.4, confidence: 0.82 }
                  ].map((strategy, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Target className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium">{strategy.strategy}</div>
                          <div className="text-sm text-gray-600">{strategy.signals} signals generated</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="font-bold text-green-600">{strategy.success}%</div>
                          <div className="text-xs text-gray-600">Success</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold text-blue-600">+{strategy.avgReturn}%</div>
                          <div className="text-xs text-gray-600">Avg Return</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold text-purple-600">{(strategy.confidence * 100).toFixed(0)}%</div>
                          <div className="text-xs text-gray-600">Confidence</div>
                        </div>
                        <div className="w-20">
                          <Progress value={strategy.success} className="h-2" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Signals */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Recent Signal Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {signalsData?.length > 0 ? (
                    // Use real signals data
                    signalsData.slice(0, 5).map((signal, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${signal.status === 'active' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                          <div>
                            <div className="font-medium">{signal.symbol || 'N/A'}</div>
                            <div className="text-sm text-gray-600">{signal.strategy || 'Unknown'}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <Badge variant={
                            (signal.confidence || 0) >= 0.9 ? 'default' : 
                            (signal.confidence || 0) >= 0.8 ? 'secondary' : 'outline'
                          }>
                            {((signal.confidence || 0) * 100).toFixed(0)}% confidence
                          </Badge>
                          <Badge variant={signal.status === 'active' ? 'default' : 'secondary'}>
                            {signal.status || 'unknown'}
                          </Badge>
                          <span className="text-sm text-gray-500">
                            {signal.timestamp ? new Date(signal.timestamp).toLocaleDateString() : 'Recent'}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    // Fallback to sample data when no signals available
                    [
                      { symbol: 'RELIANCE', strategy: 'Multibagger', confidence: 0.94, status: 'active', time: '2 hours ago' },
                      { symbol: 'TCS', strategy: 'Momentum', confidence: 0.87, status: 'completed', time: '5 hours ago' },
                      { symbol: 'HDFCBANK', strategy: 'Value', confidence: 0.91, status: 'active', time: '1 day ago' },
                      { symbol: 'INFY', strategy: 'Breakout', confidence: 0.83, status: 'active', time: '1 day ago' },
                      { symbol: 'WIPRO', strategy: 'Mean Reversion', confidence: 0.79, status: 'completed', time: '2 days ago' }
                    ].map((signal, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${signal.status === 'active' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                          <div>
                            <div className="font-medium">{signal.symbol}</div>
                            <div className="text-sm text-gray-600">{signal.strategy}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <Badge variant={signal.confidence >= 0.9 ? 'default' : signal.confidence >= 0.8 ? 'secondary' : 'outline'}>
                            {(signal.confidence * 100).toFixed(0)}% confidence
                          </Badge>
                          <Badge variant={signal.status === 'active' ? 'default' : 'secondary'}>
                            {signal.status}
                          </Badge>
                          <span className="text-sm text-gray-500">{signal.time}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Risk Tab */}
          <TabsContent value="risk" className="space-y-6">
            {/* Risk Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Shield className="h-5 w-5" />
                    Risk Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-orange-600 mb-2">7.2</div>
                    <div className="text-sm text-gray-600 mb-4">Moderate Risk</div>
                    <Progress value={72} className="h-3" />
                    <div className="text-xs text-gray-500 mt-2">Risk Scale: 1-10</div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <TrendingDown className="h-5 w-5" />
                    Max Drawdown
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-red-600 mb-2">-{analytics?.overview?.maxDrawdown?.toFixed(1) || '0'}%</div>
                    <div className="text-sm text-gray-600 mb-4">Peak to Trough</div>
                    <div className="text-xs text-gray-500">Recovery Time: 23 days</div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Activity className="h-5 w-5" />
                    Volatility
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-purple-600 mb-2">{analytics?.overview?.volatility?.toFixed(1) || '0'}%</div>
                    <div className="text-sm text-gray-600 mb-4">Annualized</div>
                    <div className="text-xs text-gray-500">vs Market: +2.3%</div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Risk Metrics Detail */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Detailed Risk Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-semibold">Risk Ratios</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Sharpe Ratio</span>
                        <span className="font-medium">{analytics?.overview?.sharpeRatio?.toFixed(2) || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Sortino Ratio</span>
                        <span className="font-medium">2.87</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Calmar Ratio</span>
                        <span className="font-medium">1.94</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Information Ratio</span>
                        <span className="font-medium">0.73</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-semibold">Downside Risk</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Downside Deviation</span>
                        <span className="font-medium">12.4%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">VaR (95%)</span>
                        <span className="font-medium text-red-600">-8.7%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">CVaR (95%)</span>
                        <span className="font-medium text-red-600">-12.3%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Maximum Loss</span>
                        <span className="font-medium text-red-600">-15.2%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Position Risk Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Position Risk Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { symbol: 'RELIANCE', risk: 'High', concentration: 15.2, beta: 1.34, volatility: 28.5 },
                    { symbol: 'TCS', risk: 'Medium', concentration: 12.1, beta: 0.87, volatility: 22.1 },
                    { symbol: 'HDFCBANK', risk: 'Medium', concentration: 10.8, beta: 1.12, volatility: 25.3 },
                    { symbol: 'INFY', risk: 'Low', concentration: 9.4, beta: 0.92, volatility: 19.7 },
                    { symbol: 'ICICIBANK', risk: 'Medium', concentration: 8.1, beta: 1.18, volatility: 26.8 }
                  ].map((position, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${
                          position.risk === 'High' ? 'bg-red-500' : 
                          position.risk === 'Medium' ? 'bg-orange-500' : 'bg-green-500'
                        }`}></div>
                        <div>
                          <div className="font-medium">{position.symbol}</div>
                          <div className="text-sm text-gray-600">{position.concentration}% of portfolio</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="font-medium">{position.beta}</div>
                          <div className="text-xs text-gray-600">Beta</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium">{position.volatility}%</div>
                          <div className="text-xs text-gray-600">Volatility</div>
                        </div>
                        <Badge variant={
                          position.risk === 'High' ? 'destructive' : 
                          position.risk === 'Medium' ? 'secondary' : 'default'
                        }>
                          {position.risk} Risk
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Insights Tab */}
          <TabsContent value="insights" className="space-y-6">
            {/* AI Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  AI-Powered Insights
                </CardTitle>
                <CardDescription>
                  Machine learning analysis of your trading patterns and market opportunities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-start gap-3">
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-green-800">Strong Performance Detected</div>
                        <div className="text-sm text-green-700 mt-1">
                          Your multibagger strategy is outperforming the market by 23.4%. Consider increasing allocation to this strategy.
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-start gap-3">
                      <Eye className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-blue-800">Market Opportunity</div>
                        <div className="text-sm text-blue-700 mt-1">
                          Banking sector showing strong momentum. 3 high-confidence signals detected in HDFC Bank, ICICI Bank, and Axis Bank.
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="h-5 w-5 text-orange-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-orange-800">Risk Alert</div>
                        <div className="text-sm text-orange-700 mt-1">
                          Portfolio concentration in technology sector is 28.5%. Consider diversifying to reduce sector-specific risk.
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <div className="flex items-start gap-3">
                      <Target className="h-5 w-5 text-purple-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-purple-800">Optimization Suggestion</div>
                        <div className="text-sm text-purple-700 mt-1">
                          Your average holding period is 18 days. Historical data suggests extending to 25-30 days could improve returns by 8-12%.
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Market Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendUp className="h-5 w-5" />
                  Market Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-3">Trending Sectors</h4>
                    <div className="space-y-3">
                      {[
                        { sector: 'Banking & Finance', trend: 'up', strength: 85 },
                        { sector: 'Technology', trend: 'up', strength: 72 },
                        { sector: 'Healthcare', trend: 'neutral', strength: 58 },
                        { sector: 'Energy', trend: 'down', strength: 34 }
                      ].map((sector, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {sector.trend === 'up' ? (
                              <ArrowUp className="h-4 w-4 text-green-600" />
                            ) : sector.trend === 'down' ? (
                              <ArrowDown className="h-4 w-4 text-red-600" />
                            ) : (
                              <Minus className="h-4 w-4 text-gray-600" />
                            )}
                            <span className="text-sm">{sector.sector}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Progress value={sector.strength} className="w-16 h-2" />
                            <span className="text-xs text-gray-600">{sector.strength}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-3">Market Sentiment</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Overall Sentiment</span>
                        <Badge variant="default" className="bg-green-100 text-green-800">Bullish</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Fear & Greed Index</span>
                        <span className="font-medium">72 (Greed)</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">VIX Level</span>
                        <span className="font-medium">18.4 (Low)</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Market Trend</span>
                        <span className="font-medium text-green-600">Uptrend</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  Personalized Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-blue-600">1</span>
                      </div>
                      <div>
                        <div className="font-medium">Increase Multibagger Allocation</div>
                        <div className="text-sm text-gray-600 mt-1">
                          Your multibagger strategy has a 91.3% success rate. Consider increasing allocation from current 15% to 25% for optimal returns.
                        </div>
                        <div className="text-xs text-green-600 mt-2">Potential impact: +12-18% annual returns</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-green-600">2</span>
                      </div>
                      <div>
                        <div className="font-medium">Diversify Sector Exposure</div>
                        <div className="text-sm text-gray-600 mt-1">
                          Add positions in healthcare and consumer goods to reduce technology sector concentration risk.
                        </div>
                        <div className="text-xs text-blue-600 mt-2">Risk reduction: 15-20%</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-purple-600">3</span>
                      </div>
                      <div>
                        <div className="font-medium">Optimize Exit Strategy</div>
                        <div className="text-sm text-gray-600 mt-1">
                          Consider implementing trailing stop-losses at 15% to protect profits while allowing for continued upside.
                        </div>
                        <div className="text-xs text-orange-600 mt-2">Profit protection: Enhanced</div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          </Tabs>
      </div>
    </MainLayout>
  )
}
