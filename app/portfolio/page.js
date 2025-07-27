'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Briefcase, 
  TrendingUp, 
  TrendingDown, 
  DollarSign,
  PieChart,
  BarChart3,
  Target,
  Shield,
  Clock,
  AlertTriangle,
  CheckCircle,
  Activity,
  Zap,
  RefreshCw
} from 'lucide-react'

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState(null)
  const [positions, setPositions] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  // Mock portfolio data
  const mockPortfolio = {
    totalValue: 2456789,
    totalInvested: 1850000,
    totalPnL: 606789,
    totalPnLPercent: 32.8,
    dayPnL: 23456,
    dayPnLPercent: 0.96,
    activePositions: 12,
    completedTrades: 45,
    winRate: 78.3,
    bestPerformer: { symbol: 'CLEAN', return: 287.5 },
    worstPerformer: { symbol: 'IDEA', return: -12.3 },
    allocation: [
      { strategy: 'Multibagger', value: 1234567, percentage: 50.3, color: '#3B82F6' },
      { strategy: 'Momentum', value: 654321, percentage: 26.6, color: '#10B981' },
      { strategy: 'Swing', value: 345678, percentage: 14.1, color: '#F59E0B' },
      { strategy: 'Breakout', value: 222223, percentage: 9.0, color: '#EF4444' }
    ],
    riskMetrics: {
      sharpeRatio: 2.34,
      maxDrawdown: 15.2,
      volatility: 24.8,
      beta: 1.12
    }
  }

  const mockPositions = [
    {
      id: 1,
      symbol: 'RELIANCE',
      strategy: 'multibagger',
      quantity: 100,
      avgPrice: 2456.75,
      currentPrice: 2478.30,
      invested: 245675,
      currentValue: 247830,
      pnl: 2155,
      pnlPercent: 0.88,
      dayChange: 21.55,
      dayChangePercent: 0.88,
      entryDate: '2024-12-15',
      targetPrice: 4913.50,
      stopLoss: 1965.40,
      status: 'active'
    },
    {
      id: 2,
      symbol: 'TCS',
      strategy: 'momentum',
      quantity: 50,
      avgPrice: 3789.20,
      currentPrice: 3801.45,
      invested: 189460,
      currentValue: 190072.50,
      pnl: 612.50,
      pnlPercent: 0.32,
      dayChange: 12.25,
      dayChangePercent: 0.32,
      entryDate: '2025-01-10',
      targetPrice: 4167.12,
      stopLoss: 3410.28,
      status: 'active'
    },
    {
      id: 3,
      symbol: 'INFY',
      strategy: 'swing',
      quantity: 200,
      avgPrice: 1456.30,
      currentPrice: 1612.45,
      invested: 291260,
      currentValue: 322490,
      pnl: 31230,
      pnlPercent: 10.72,
      dayChange: 156.15,
      dayChangePercent: 10.72,
      entryDate: '2024-11-20',
      targetPrice: 1602.93,
      stopLoss: 1310.67,
      status: 'target_hit'
    },
    {
      id: 4,
      symbol: 'WIPRO',
      strategy: 'multibagger',
      quantity: 300,
      avgPrice: 445.60,
      currentPrice: 467.80,
      invested: 133680,
      currentValue: 140340,
      pnl: 6660,
      pnlPercent: 4.98,
      dayChange: 22.20,
      dayChangePercent: 4.98,
      entryDate: '2024-10-05',
      targetPrice: 891.20,
      stopLoss: 356.48,
      status: 'active'
    },
    {
      id: 5,
      symbol: 'HDFC',
      strategy: 'swing',
      quantity: 75,
      avgPrice: 1678.90,
      currentPrice: 1734.25,
      invested: 125917.50,
      currentValue: 130068.75,
      pnl: 4151.25,
      pnlPercent: 3.30,
      dayChange: 55.35,
      dayChangePercent: 3.30,
      entryDate: '2025-01-05',
      targetPrice: 1846.79,
      stopLoss: 1511.01,
      status: 'active'
    }
  ]

  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setPortfolio(mockPortfolio)
      setPositions(mockPositions)
      setLoading(false)
    }, 1000)
  }, [])

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Active</Badge>
      case 'target_hit':
        return <Badge variant="default" className="bg-green-100 text-green-800">Target Hit</Badge>
      case 'stop_loss':
        return <Badge variant="destructive">Stop Loss</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const getStrategyIcon = (strategy) => {
    switch (strategy) {
      case 'multibagger': return <Target className="h-4 w-4" />
      case 'momentum': return <TrendingUp className="h-4 w-4" />
      case 'swing': return <Activity className="h-4 w-4" />
      case 'breakout': return <Zap className="h-4 w-4" />
      default: return <BarChart3 className="h-4 w-4" />
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const PositionCard = ({ position }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              {getStrategyIcon(position.strategy)}
            </div>
            <div>
              <h3 className="font-semibold text-lg">{position.symbol}</h3>
              <p className="text-sm text-gray-600 capitalize">{position.strategy} • {position.quantity} shares</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusBadge(position.status)}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600">Invested</p>
            <p className="font-semibold">{formatCurrency(position.invested)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Current Value</p>
            <p className="font-semibold">{formatCurrency(position.currentValue)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-gray-600">P&L</p>
            <div className="flex items-center space-x-2">
              <p className={`font-bold ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(position.pnl)}
              </p>
              <div className="flex items-center">
                {position.pnl >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-sm font-medium ml-1 ${
                  position.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {position.pnl >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Entry Date</p>
            <p className="font-semibold">{new Date(position.entryDate).toLocaleDateString()}</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 text-sm mb-4">
          <div>
            <p className="text-gray-600">Avg Price</p>
            <p className="font-semibold">₹{position.avgPrice.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-gray-600">Current</p>
            <p className="font-semibold">₹{position.currentPrice.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-gray-600">Target</p>
            <p className="font-semibold text-green-600">₹{position.targetPrice.toFixed(2)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="h-4 w-4 mr-1" />
            {Math.floor((new Date() - new Date(position.entryDate)) / (1000 * 60 * 60 * 24))} days
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              View Chart
            </Button>
            <Button size="sm">
              Manage
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const AllocationChart = ({ data }) => (
    <div className="space-y-4">
      {data.map((item, index) => (
        <div key={index} className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="font-medium">{item.strategy}</span>
            <div className="text-right">
              <span className="font-bold">{formatCurrency(item.value)}</span>
              <span className="text-sm text-gray-600 ml-2">({item.percentage}%)</span>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full"
              style={{ 
                width: `${item.percentage}%`, 
                backgroundColor: item.color 
              }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  )

  if (loading) {
    return (
      <MainLayout>
        <div className="p-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
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
            <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
            <p className="text-gray-600 mt-2">
              Track your investments, monitor performance, and manage positions.
            </p>
          </div>
          <Button>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Data
          </Button>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Value</p>
                  <p className="text-2xl font-bold">{portfolio ? formatCurrency(portfolio.totalValue) : '₹0'}</p>
                </div>
                <Briefcase className="h-8 w-8 text-blue-500" />
              </div>
              <div className="mt-2 flex items-center">
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-sm text-green-600 font-medium">
                  +{portfolio?.dayPnLPercent || 0}% today
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total P&L</p>
                  <p className="text-2xl font-bold text-green-600">
                    {portfolio ? formatCurrency(portfolio.totalPnL) : '₹0'}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-green-600 font-medium">
                  +{portfolio?.totalPnLPercent || 0}% overall
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Positions</p>
                  <p className="text-2xl font-bold">{portfolio?.activePositions || 0}</p>
                </div>
                <Target className="h-8 w-8 text-purple-500" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  {portfolio?.completedTrades || 0} completed
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Win Rate</p>
                  <p className="text-2xl font-bold text-green-600">{portfolio?.winRate || 0}%</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  Success rate
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analysis */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 max-w-2xl">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="positions">Positions</TabsTrigger>
            <TabsTrigger value="allocation">Allocation</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Best & Worst Performers</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                    <div>
                      <p className="font-semibold text-green-800">Best Performer</p>
                      <p className="text-sm text-green-600">{portfolio?.bestPerformer?.symbol || 'N/A'}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold text-green-600">
                        +{portfolio?.bestPerformer?.return || 0}%
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                    <div>
                      <p className="font-semibold text-red-800">Worst Performer</p>
                      <p className="text-sm text-red-600">{portfolio?.worstPerformer?.symbol || 'N/A'}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold text-red-600">
                        {portfolio?.worstPerformer?.return || 0}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Risk Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Sharpe Ratio</span>
                    <span className="font-bold">{portfolio?.riskMetrics?.sharpeRatio || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Max Drawdown</span>
                    <span className="font-bold text-red-600">{portfolio?.riskMetrics?.maxDrawdown || 0}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Volatility</span>
                    <span className="font-bold">{portfolio?.riskMetrics?.volatility || 0}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Beta</span>
                    <span className="font-bold">{portfolio?.riskMetrics?.beta || 'N/A'}</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="positions" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {positions.map((position) => (
                <PositionCard key={position.id} position={position} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="allocation" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Strategy Allocation</CardTitle>
                  <CardDescription>Portfolio distribution across trading strategies</CardDescription>
                </CardHeader>
                <CardContent>
                  <AllocationChart data={portfolio?.allocation || []} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Allocation Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {(portfolio?.allocation || []).map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div 
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: item.color }}
                          ></div>
                          <span className="font-medium">{item.strategy}</span>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{item.percentage}%</p>
                          <p className="text-sm text-gray-600">{formatCurrency(item.value)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="space-y-6 mt-6">
            <Card>
              <CardContent className="p-12 text-center">
                <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Performance Charts</h3>
                <p className="text-gray-600 mb-4">
                  Detailed performance charts and analytics will be available here.
                </p>
                <Button>
                  <BarChart3 className="h-4 w-4 mr-2" />
                  View Analytics
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
