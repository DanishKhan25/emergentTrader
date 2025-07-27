'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
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
  Users
} from 'lucide-react'

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [timeRange, setTimeRange] = useState('6m')
  const [selectedStrategy, setSelectedStrategy] = useState('all')
  const [activeTab, setActiveTab] = useState('overview')

  // Mock analytics data
  const mockAnalytics = {
    overview: {
      totalSignals: 1247,
      successfulSignals: 1087,
      successRate: 87.2,
      totalReturn: 2456789,
      avgReturn: 34.7,
      bestReturn: 28700,
      worstReturn: -12.3,
      avgHoldingPeriod: 8.4,
      sharpeRatio: 2.34,
      maxDrawdown: 15.2,
      volatility: 24.8
    },
    strategyPerformance: [
      {
        strategy: 'Multibagger',
        signals: 156,
        successRate: 87.2,
        avgReturn: 1828,
        totalReturn: 285168,
        bestReturn: 28700,
        color: '#3B82F6'
      },
      {
        strategy: 'Momentum',
        signals: 287,
        successRate: 73.2,
        avgReturn: 24.5,
        totalReturn: 70315,
        bestReturn: 156,
        color: '#10B981'
      },
      {
        strategy: 'Swing',
        signals: 423,
        successRate: 68.1,
        avgReturn: 12.8,
        totalReturn: 54144,
        bestReturn: 78,
        color: '#F59E0B'
      },
      {
        strategy: 'Breakout',
        signals: 198,
        successRate: 71.2,
        avgReturn: 18.9,
        totalReturn: 37422,
        bestReturn: 124,
        color: '#EF4444'
      }
    ],
    monthlyPerformance: [
      { month: 'Aug 2024', signals: 89, returns: 234567, successRate: 84.3 },
      { month: 'Sep 2024', signals: 76, returns: 345678, successRate: 86.8 },
      { month: 'Oct 2024', signals: 92, returns: 456789, successRate: 88.0 },
      { month: 'Nov 2024', signals: 103, returns: 567890, successRate: 89.3 },
      { month: 'Dec 2024', signals: 87, returns: 678901, successRate: 85.1 },
      { month: 'Jan 2025', signals: 94, returns: 789012, successRate: 87.2 }
    ],
    topPerformers: [
      { symbol: 'CLEAN', strategy: 'Multibagger', return: 28700, period: '18 months', invested: 50000 },
      { symbol: 'APLAPOLLO', strategy: 'Multibagger', return: 7045, period: '14 months', invested: 75000 },
      { symbol: 'RATNAMANI', strategy: 'Multibagger', return: 5012, period: '16 months', invested: 60000 },
      { symbol: 'BHARTIARTL', strategy: 'Breakout', return: 124, period: '6 weeks', invested: 100000 },
      { symbol: 'RELIANCE', strategy: 'Momentum', return: 156, period: '2 months', invested: 80000 }
    ],
    sectorAnalysis: [
      { sector: 'Technology', signals: 234, successRate: 89.3, avgReturn: 45.2, allocation: 28.5 },
      { sector: 'Financial Services', signals: 187, successRate: 82.4, avgReturn: 32.1, allocation: 22.8 },
      { sector: 'Healthcare', signals: 156, successRate: 91.0, avgReturn: 67.8, allocation: 18.9 },
      { sector: 'Consumer Goods', signals: 143, successRate: 78.9, avgReturn: 28.4, allocation: 16.2 },
      { sector: 'Industrial', signals: 98, successRate: 85.7, avgReturn: 41.3, allocation: 13.6 }
    ],
    riskAnalysis: {
      portfolioRisk: 'Medium-High',
      diversificationScore: 8.4,
      concentrationRisk: 'Low',
      correlationRisk: 'Medium',
      liquidityRisk: 'Low',
      recommendations: [
        'Consider reducing exposure to high-beta stocks',
        'Increase diversification across sectors',
        'Monitor correlation between positions',
        'Maintain adequate cash reserves'
      ]
    }
  }

  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setAnalytics(mockAnalytics)
      setLoading(false)
    }, 1000)
  }, [timeRange, selectedStrategy])

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const PerformanceCard = ({ title, value, change, icon: Icon, color = 'blue' }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {change && (
              <div className="flex items-center mt-1">
                {change >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                )}
                <span className={`text-sm font-medium ${
                  change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {change >= 0 ? '+' : ''}{change}%
                </span>
              </div>
            )}
          </div>
          <Icon className={`h-8 w-8 text-${color}-500`} />
        </div>
      </CardContent>
    </Card>
  )

  const StrategyChart = ({ data }) => (
    <div className="space-y-4">
      {data.map((item, index) => (
        <div key={index} className="p-4 border rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div 
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: item.color }}
              ></div>
              <h3 className="font-semibold">{item.strategy}</h3>
            </div>
            <Badge variant="outline">{item.signals} signals</Badge>
          </div>
          
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Success Rate</p>
              <p className="font-bold text-green-600">{item.successRate}%</p>
            </div>
            <div>
              <p className="text-gray-600">Avg Return</p>
              <p className="font-bold">{item.avgReturn}%</p>
            </div>
            <div>
              <p className="text-gray-600">Total Return</p>
              <p className="font-bold text-blue-600">{formatCurrency(item.totalReturn)}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )

  const MonthlyChart = ({ data }) => (
    <div className="space-y-3">
      {data.map((item, index) => (
        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <p className="font-medium">{item.month}</p>
            <p className="text-sm text-gray-600">{item.signals} signals • {item.successRate}% success</p>
          </div>
          <div className="text-right">
            <p className="font-bold text-green-600">{formatCurrency(item.returns)}</p>
          </div>
        </div>
      ))}
    </div>
  )

  const TopPerformersTable = ({ data }) => (
    <div className="space-y-3">
      {data.map((item, index) => (
        <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold text-blue-600">{index + 1}</span>
            </div>
            <div>
              <p className="font-semibold">{item.symbol}</p>
              <p className="text-sm text-gray-600">{item.strategy} • {item.period}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="font-bold text-green-600">+{item.return}%</p>
            <p className="text-sm text-gray-600">{formatCurrency(item.invested)} invested</p>
          </div>
        </div>
      ))}
    </div>
  )

  const SectorAnalysisTable = ({ data }) => (
    <div className="space-y-3">
      {data.map((item, index) => (
        <div key={index} className="p-4 border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold">{item.sector}</h3>
            <Badge variant="outline">{item.allocation}% allocation</Badge>
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Signals</p>
              <p className="font-bold">{item.signals}</p>
            </div>
            <div>
              <p className="text-gray-600">Success Rate</p>
              <p className="font-bold text-green-600">{item.successRate}%</p>
            </div>
            <div>
              <p className="text-gray-600">Avg Return</p>
              <p className="font-bold text-blue-600">{item.avgReturn}%</p>
            </div>
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
            <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600 mt-2">
              Comprehensive performance analysis and insights for your trading strategies.
            </p>
          </div>
          <div className="flex space-x-3">
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
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <PerformanceCard
            title="Total Signals"
            value={analytics.overview.totalSignals.toLocaleString()}
            change={5.2}
            icon={Target}
            color="blue"
          />
          <PerformanceCard
            title="Success Rate"
            value={`${analytics.overview.successRate}%`}
            change={2.1}
            icon={Award}
            color="green"
          />
          <PerformanceCard
            title="Total Returns"
            value={formatCurrency(analytics.overview.totalReturn)}
            change={12.8}
            icon={DollarSign}
            color="purple"
          />
          <PerformanceCard
            title="Avg Return"
            value={`${analytics.overview.avgReturn}%`}
            change={-1.3}
            icon={Percent}
            color="orange"
          />
        </div>

        {/* Detailed Analytics */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5 max-w-3xl">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="strategies">Strategies</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="sectors">Sectors</TabsTrigger>
            <TabsTrigger value="risk">Risk</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Performance Summary</CardTitle>
                  <CardDescription>Key performance indicators</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Best Return</span>
                    <span className="font-bold text-green-600">+{analytics.overview.bestReturn}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Worst Return</span>
                    <span className="font-bold text-red-600">{analytics.overview.worstReturn}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Avg Holding Period</span>
                    <span className="font-bold">{analytics.overview.avgHoldingPeriod} months</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Sharpe Ratio</span>
                    <span className="font-bold">{analytics.overview.sharpeRatio}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Max Drawdown</span>
                    <span className="font-bold text-red-600">{analytics.overview.maxDrawdown}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Volatility</span>
                    <span className="font-bold">{analytics.overview.volatility}%</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Top Performers</CardTitle>
                  <CardDescription>Best performing signals</CardDescription>
                </CardHeader>
                <CardContent>
                  <TopPerformersTable data={analytics.topPerformers.slice(0, 5)} />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="strategies" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Strategy Performance Comparison</CardTitle>
                <CardDescription>Performance metrics across all trading strategies</CardDescription>
              </CardHeader>
              <CardContent>
                <StrategyChart data={analytics.strategyPerformance} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="performance" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Monthly Performance</CardTitle>
                <CardDescription>Returns and signal count by month</CardDescription>
              </CardHeader>
              <CardContent>
                <MonthlyChart data={analytics.monthlyPerformance} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sectors" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Sector Analysis</CardTitle>
                <CardDescription>Performance breakdown by market sectors</CardDescription>
              </CardHeader>
              <CardContent>
                <SectorAnalysisTable data={analytics.sectorAnalysis} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="risk" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Risk Assessment</CardTitle>
                  <CardDescription>Portfolio risk analysis</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Portfolio Risk</span>
                    <Badge className="bg-orange-100 text-orange-800">
                      {analytics.riskAnalysis.portfolioRisk}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Diversification Score</span>
                    <span className="font-bold text-green-600">{analytics.riskAnalysis.diversificationScore}/10</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Concentration Risk</span>
                    <Badge className="bg-green-100 text-green-800">
                      {analytics.riskAnalysis.concentrationRisk}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Correlation Risk</span>
                    <Badge className="bg-yellow-100 text-yellow-800">
                      {analytics.riskAnalysis.correlationRisk}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Liquidity Risk</span>
                    <Badge className="bg-green-100 text-green-800">
                      {analytics.riskAnalysis.liquidityRisk}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Risk Recommendations</CardTitle>
                  <CardDescription>Suggestions to optimize risk profile</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {analytics.riskAnalysis.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
