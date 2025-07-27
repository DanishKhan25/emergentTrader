'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TrendingUp, 
  TrendingDown, 
  Star,
  StarOff,
  Target,
  Shield,
  BarChart3,
  Activity,
  DollarSign,
  Percent,
  Calendar,
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'
import Link from 'next/link'

export default function StockDetailPage() {
  const params = useParams()
  const symbol = params.symbol
  const [stock, setStock] = useState(null)
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(false)
  const [isWatchlisted, setIsWatchlisted] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  // Mock stock data
  const mockStock = {
    symbol: symbol?.toUpperCase() || 'RELIANCE',
    name: 'Reliance Industries Limited',
    sector: 'Oil & Gas',
    industry: 'Refineries',
    marketCap: 1658900000000,
    price: 2456.75,
    change: 23.45,
    changePercent: 0.96,
    dayHigh: 2478.90,
    dayLow: 2445.20,
    volume: 1234567,
    avgVolume: 987654,
    pe: 24.5,
    pb: 2.1,
    eps: 100.27,
    dividend: 8.5,
    dividendYield: 0.35,
    roe: 12.8,
    debt: 0.45,
    isShariahCompliant: true,
    fundamentals: {
      revenue: 792000000000,
      revenueGrowth: 23.4,
      profit: 67845000000,
      profitGrowth: 28.7,
      operatingMargin: 12.5,
      netMargin: 8.6,
      currentRatio: 1.2,
      quickRatio: 0.8,
      debtToEquity: 0.45,
      returnOnAssets: 6.2,
      returnOnEquity: 12.8,
      bookValue: 1167.45
    },
    technicals: {
      sma20: 2398.45,
      sma50: 2367.89,
      sma200: 2234.56,
      rsi: 58.7,
      macd: 12.34,
      bollinger: {
        upper: 2489.67,
        middle: 2456.78,
        lower: 2423.89
      },
      support: 2400.00,
      resistance: 2500.00,
      trend: 'bullish'
    },
    news: [
      {
        title: 'Reliance Industries reports strong Q3 results',
        summary: 'Company beats estimates with 28% profit growth',
        date: '2025-01-25',
        sentiment: 'positive'
      },
      {
        title: 'New petrochemical plant expansion announced',
        summary: 'Investment of ₹15,000 crores for capacity expansion',
        date: '2025-01-20',
        sentiment: 'positive'
      },
      {
        title: 'Jio subscriber growth continues strong momentum',
        summary: 'Added 12 million subscribers in Q3',
        date: '2025-01-18',
        sentiment: 'positive'
      }
    ]
  }

  const mockSignals = [
    {
      id: 1,
      strategy: 'multibagger',
      signalType: 'BUY',
      entryPrice: 2456.75,
      targetPrice: 4913.50,
      stopLoss: 1965.40,
      confidence: 0.87,
      generatedAt: '2025-01-27T09:15:00Z',
      status: 'active',
      timeframe: '6-12 months',
      reasoning: 'Strong fundamentals with revenue growth >20% and expanding market share in telecom'
    },
    {
      id: 2,
      strategy: 'momentum',
      signalType: 'BUY',
      entryPrice: 2445.30,
      targetPrice: 2689.83,
      stopLoss: 2200.77,
      confidence: 0.73,
      generatedAt: '2025-01-20T09:15:00Z',
      status: 'completed',
      timeframe: '1-3 months',
      reasoning: 'Breakout above 20-day SMA with strong volume surge'
    }
  ]

  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setStock(mockStock)
      setSignals(mockSignals)
      setLoading(false)
    }, 1000)
  }, [symbol])

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatMarketCap = (value) => {
    if (value >= 1e12) return `₹${(value / 1e12).toFixed(2)}T`
    if (value >= 1e9) return `₹${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `₹${(value / 1e6).toFixed(2)}M`
    return `₹${value}`
  }

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'bullish': return 'text-green-600 bg-green-100'
      case 'bearish': return 'text-red-600 bg-red-100'
      case 'neutral': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getSignalStatus = (status) => {
    switch (status) {
      case 'active':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Active</Badge>
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800">Completed</Badge>
      case 'stopped':
        return <Badge variant="destructive">Stopped</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="p-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </MainLayout>
    )
  }

  if (!stock) {
    return (
      <MainLayout>
        <div className="p-6">
          <Card>
            <CardContent className="p-12 text-center">
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Stock Not Found</h3>
              <p className="text-gray-600 mb-4">The stock symbol "{symbol}" was not found.</p>
              <Link href="/stocks">
                <Button>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Stocks
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Link href="/stocks">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <div>
              <div className="flex items-center space-x-3">
                <h1 className="text-3xl font-bold text-gray-900">{stock.symbol}</h1>
                {stock.isShariahCompliant && (
                  <Badge variant="secondary" className="text-green-700 bg-green-100">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Shariah
                  </Badge>
                )}
              </div>
              <p className="text-gray-600 mt-1">{stock.name}</p>
              <p className="text-sm text-gray-500">{stock.sector} • {stock.industry}</p>
            </div>
          </div>
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={() => setIsWatchlisted(!isWatchlisted)}
            >
              {isWatchlisted ? (
                <>
                  <Star className="h-4 w-4 mr-2 fill-current" />
                  Watchlisted
                </>
              ) : (
                <>
                  <StarOff className="h-4 w-4 mr-2" />
                  Add to Watchlist
                </>
              )}
            </Button>
            <Button>
              <Target className="h-4 w-4 mr-2" />
              Generate Signal
            </Button>
          </div>
        </div>

        {/* Price Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Current Price</p>
                  <p className="text-3xl font-bold">{formatCurrency(stock.price)}</p>
                </div>
                <DollarSign className="h-8 w-8 text-blue-500" />
              </div>
              <div className="mt-2 flex items-center">
                {stock.change >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                )}
                <span className={`text-sm font-medium ${
                  stock.change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Market Cap</p>
                  <p className="text-2xl font-bold">{formatMarketCap(stock.marketCap)}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-purple-500" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">P/E: {stock.pe}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Volume</p>
                  <p className="text-2xl font-bold">{stock.volume.toLocaleString()}</p>
                </div>
                <Activity className="h-8 w-8 text-orange-500" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">Avg: {stock.avgVolume.toLocaleString()}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Day Range</p>
                  <p className="text-lg font-bold">
                    {formatCurrency(stock.dayLow)} - {formatCurrency(stock.dayHigh)}
                  </p>
                </div>
                <Percent className="h-8 w-8 text-green-500" />
              </div>
              <div className="mt-2">
                <Badge className={getTrendColor(stock.technicals.trend)}>
                  {stock.technicals.trend}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analysis */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5 max-w-3xl">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="fundamentals">Fundamentals</TabsTrigger>
            <TabsTrigger value="technicals">Technicals</TabsTrigger>
            <TabsTrigger value="signals">Signals</TabsTrigger>
            <TabsTrigger value="news">News</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Key Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">P/E Ratio</p>
                      <p className="font-bold">{stock.pe}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">P/B Ratio</p>
                      <p className="font-bold">{stock.pb}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">EPS</p>
                      <p className="font-bold">₹{stock.eps}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Dividend</p>
                      <p className="font-bold">₹{stock.dividend}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">ROE</p>
                      <p className="font-bold">{stock.roe}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Debt Ratio</p>
                      <p className="font-bold">{stock.debt}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Company Info</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600">Sector</p>
                    <p className="font-semibold">{stock.sector}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Industry</p>
                    <p className="font-semibold">{stock.industry}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Market Cap</p>
                    <p className="font-semibold">{formatMarketCap(stock.marketCap)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Shariah Compliant</p>
                    <div className="flex items-center">
                      {stock.isShariahCompliant ? (
                        <>
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                          <span className="text-green-600 font-semibold">Yes</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="h-4 w-4 text-red-500 mr-2" />
                          <span className="text-red-600 font-semibold">No</span>
                        </>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="fundamentals" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Financial Performance</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Revenue</p>
                      <p className="font-bold">{formatMarketCap(stock.fundamentals.revenue)}</p>
                      <p className="text-sm text-green-600">+{stock.fundamentals.revenueGrowth}% YoY</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Profit</p>
                      <p className="font-bold">{formatMarketCap(stock.fundamentals.profit)}</p>
                      <p className="text-sm text-green-600">+{stock.fundamentals.profitGrowth}% YoY</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Operating Margin</p>
                      <p className="font-bold">{stock.fundamentals.operatingMargin}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Net Margin</p>
                      <p className="font-bold">{stock.fundamentals.netMargin}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Financial Health</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Current Ratio</p>
                      <p className="font-bold">{stock.fundamentals.currentRatio}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Quick Ratio</p>
                      <p className="font-bold">{stock.fundamentals.quickRatio}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Debt to Equity</p>
                      <p className="font-bold">{stock.fundamentals.debtToEquity}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">ROA</p>
                      <p className="font-bold">{stock.fundamentals.returnOnAssets}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="technicals" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Moving Averages</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>SMA 20</span>
                      <span className="font-bold">{formatCurrency(stock.technicals.sma20)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>SMA 50</span>
                      <span className="font-bold">{formatCurrency(stock.technicals.sma50)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>SMA 200</span>
                      <span className="font-bold">{formatCurrency(stock.technicals.sma200)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Technical Indicators</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>RSI</span>
                      <span className="font-bold">{stock.technicals.rsi}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>MACD</span>
                      <span className="font-bold">{stock.technicals.macd}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Support</span>
                      <span className="font-bold text-green-600">{formatCurrency(stock.technicals.support)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Resistance</span>
                      <span className="font-bold text-red-600">{formatCurrency(stock.technicals.resistance)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="signals" className="space-y-6 mt-6">
            <div className="space-y-4">
              {signals.map((signal) => (
                <Card key={signal.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Target className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold capitalize">{signal.strategy} Strategy</h3>
                          <p className="text-sm text-gray-600">{signal.timeframe}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getSignalStatus(signal.status)}
                        <Badge variant="outline">
                          {(signal.confidence * 100).toFixed(0)}% Confidence
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">Entry Price</p>
                        <p className="font-bold">{formatCurrency(signal.entryPrice)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Target Price</p>
                        <p className="font-bold text-green-600">{formatCurrency(signal.targetPrice)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Stop Loss</p>
                        <p className="font-bold text-red-600">{formatCurrency(signal.stopLoss)}</p>
                      </div>
                    </div>

                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700">
                        <strong>Reasoning:</strong> {signal.reasoning}
                      </p>
                    </div>

                    <div className="flex items-center justify-between mt-4 pt-4 border-t">
                      <span className="text-sm text-gray-600">
                        Generated: {new Date(signal.generatedAt).toLocaleDateString()}
                      </span>
                      <Button size="sm">Track Signal</Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="news" className="space-y-6 mt-6">
            <div className="space-y-4">
              {stock.news.map((item, index) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold mb-2">{item.title}</h3>
                        <p className="text-gray-600 mb-3">{item.summary}</p>
                        <div className="flex items-center space-x-3">
                          <span className="text-sm text-gray-500">
                            {new Date(item.date).toLocaleDateString()}
                          </span>
                          <Badge 
                            variant="outline" 
                            className={item.sentiment === 'positive' ? 'text-green-600' : 'text-red-600'}
                          >
                            {item.sentiment}
                          </Badge>
                        </div>
                      </div>
                      <Info className="h-5 w-5 text-gray-400 ml-4" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
