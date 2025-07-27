'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Target, 
  TrendingUp, 
  Activity, 
  Zap,
  BarChart3,
  PieChart,
  Shield,
  Clock,
  DollarSign,
  Award,
  TrendingDown,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState([])
  const [selectedStrategy, setSelectedStrategy] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  // Mock strategies data with comprehensive metrics
  const mockStrategies = [
    {
      id: 'multibagger',
      name: 'Multibagger Strategy',
      description: 'AI-enhanced strategy targeting 2x-10x+ returns through fundamental and technical analysis',
      icon: Target,
      successRate: 87,
      avgReturn: 1828,
      maxReturn: 28700,
      timeframe: '6-18 months',
      riskLevel: 'Medium-High',
      minInvestment: 10000,
      activeSignals: 23,
      totalSignals: 156,
      winRate: 87.2,
      avgHoldingPeriod: 14.5,
      sharpeRatio: 2.34,
      maxDrawdown: 15.2,
      volatility: 24.8,
      features: [
        'Growth analysis (Revenue >20%, Profit >25%)',
        'Financial strength (ROE >15%, Debt <0.6)',
        'Price action analysis with ML validation',
        'Market cap focus on small/mid-cap stocks',
        'Multiple target levels (2x, 3x, 5x, 10x+)'
      ],
      recentPerformance: [
        { month: 'Jan 2025', return: 23.4, signals: 12 },
        { month: 'Dec 2024', return: 45.2, signals: 18 },
        { month: 'Nov 2024', return: 67.8, signals: 15 },
        { month: 'Oct 2024', return: 34.1, signals: 21 },
        { month: 'Sep 2024', return: 89.3, signals: 9 },
        { month: 'Aug 2024', return: 12.7, signals: 14 }
      ],
      topPerformers: [
        { symbol: 'CLEAN', return: 28700, period: '18 months' },
        { symbol: 'APLAPOLLO', return: 7045, period: '14 months' },
        { symbol: 'RATNAMANI', return: 5012, period: '16 months' }
      ]
    },
    {
      id: 'momentum',
      name: 'Momentum Trading',
      description: 'Captures trending stocks with strong price momentum and volume surge',
      icon: TrendingUp,
      successRate: 73,
      avgReturn: 24.5,
      maxReturn: 156,
      timeframe: '1-3 months',
      riskLevel: 'Medium',
      minInvestment: 5000,
      activeSignals: 34,
      totalSignals: 287,
      winRate: 73.2,
      avgHoldingPeriod: 2.3,
      sharpeRatio: 1.67,
      maxDrawdown: 8.4,
      volatility: 18.2,
      features: [
        'Price momentum analysis (20/50 SMA crossover)',
        'Volume surge detection (2x average volume)',
        'Relative strength vs market index',
        'Breakout pattern recognition',
        'Quick profit booking strategy'
      ],
      recentPerformance: [
        { month: 'Jan 2025', return: 18.2, signals: 28 },
        { month: 'Dec 2024', return: 31.4, signals: 35 },
        { month: 'Nov 2024', return: 22.7, signals: 42 },
        { month: 'Oct 2024', return: 15.8, signals: 38 },
        { month: 'Sep 2024', return: 28.9, signals: 31 },
        { month: 'Aug 2024', return: 19.3, signals: 29 }
      ],
      topPerformers: [
        { symbol: 'RELIANCE', return: 156, period: '2 months' },
        { symbol: 'TCS', return: 89, period: '1.5 months' },
        { symbol: 'INFY', return: 67, period: '3 months' }
      ]
    },
    {
      id: 'swing',
      name: 'Swing Trading',
      description: 'Short to medium-term trades capturing price swings in trending markets',
      icon: Activity,
      successRate: 68,
      avgReturn: 12.8,
      maxReturn: 78,
      timeframe: '1-6 weeks',
      riskLevel: 'Medium',
      minInvestment: 3000,
      activeSignals: 45,
      totalSignals: 423,
      winRate: 68.1,
      avgHoldingPeriod: 1.2,
      sharpeRatio: 1.45,
      maxDrawdown: 6.7,
      volatility: 15.3,
      features: [
        'Support/resistance level analysis',
        'Chart pattern recognition',
        'RSI and MACD signal confirmation',
        'Risk-reward ratio optimization',
        'Quick entry and exit strategy'
      ],
      recentPerformance: [
        { month: 'Jan 2025', return: 14.3, signals: 38 },
        { month: 'Dec 2024', return: 19.7, signals: 41 },
        { month: 'Nov 2024', return: 8.2, signals: 47 },
        { month: 'Oct 2024', return: 22.1, signals: 52 },
        { month: 'Sep 2024', return: 11.6, signals: 35 },
        { month: 'Aug 2024', return: 16.8, signals: 43 }
      ],
      topPerformers: [
        { symbol: 'HDFC', return: 78, period: '4 weeks' },
        { symbol: 'ICICIBANK', return: 45, period: '3 weeks' },
        { symbol: 'AXISBANK', return: 34, period: '5 weeks' }
      ]
    },
    {
      id: 'breakout',
      name: 'Breakout Strategy',
      description: 'Identifies stocks breaking key resistance levels with high volume',
      icon: Zap,
      successRate: 71,
      avgReturn: 18.9,
      maxReturn: 124,
      timeframe: '2-8 weeks',
      riskLevel: 'Medium-High',
      minInvestment: 4000,
      activeSignals: 28,
      totalSignals: 198,
      winRate: 71.2,
      avgHoldingPeriod: 1.8,
      sharpeRatio: 1.78,
      maxDrawdown: 9.1,
      volatility: 19.7,
      features: [
        'Key resistance level breakouts',
        'Volume confirmation (3x average)',
        'Consolidation pattern analysis',
        'False breakout filtering',
        'Momentum continuation signals'
      ],
      recentPerformance: [
        { month: 'Jan 2025', return: 21.4, signals: 22 },
        { month: 'Dec 2024', return: 28.3, signals: 26 },
        { month: 'Nov 2024', return: 15.7, signals: 31 },
        { month: 'Oct 2024', return: 19.8, signals: 28 },
        { month: 'Sep 2024', return: 24.2, signals: 19 },
        { month: 'Aug 2024', return: 12.9, signals: 24 }
      ],
      topPerformers: [
        { symbol: 'BHARTIARTL', return: 124, period: '6 weeks' },
        { symbol: 'LT', return: 89, period: '4 weeks' },
        { symbol: 'MARUTI', return: 67, period: '7 weeks' }
      ]
    }
  ]

  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setStrategies(mockStrategies)
      setSelectedStrategy(mockStrategies[0])
      setLoading(false)
    }, 1000)
  }, [])

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'Low': return 'text-green-600 bg-green-100'
      case 'Medium': return 'text-yellow-600 bg-yellow-100'
      case 'Medium-High': return 'text-orange-600 bg-orange-100'
      case 'High': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const StrategyCard = ({ strategy, isSelected, onClick }) => (
    <Card 
      className={`cursor-pointer transition-all hover:shadow-md ${
        isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''
      }`}
      onClick={onClick}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <strategy.icon className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{strategy.name}</h3>
              <p className="text-sm text-gray-600">{strategy.timeframe}</p>
            </div>
          </div>
          <Badge className={getRiskColor(strategy.riskLevel)}>
            {strategy.riskLevel}
          </Badge>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600">Success Rate</p>
            <div className="flex items-center space-x-2">
              <p className="text-2xl font-bold text-green-600">{strategy.successRate}%</p>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600">Avg Return</p>
            <p className="text-2xl font-bold text-blue-600">{strategy.avgReturn}%</p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Active Signals</span>
            <span className="font-semibold">{strategy.activeSignals}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Total Signals</span>
            <span className="font-semibold">{strategy.totalSignals}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const PerformanceChart = ({ data }) => (
    <div className="space-y-3">
      {data.map((item, index) => (
        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <p className="font-medium">{item.month}</p>
            <p className="text-sm text-gray-600">{item.signals} signals</p>
          </div>
          <div className="text-right">
            <p className={`font-bold ${item.return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {item.return >= 0 ? '+' : ''}{item.return}%
            </p>
          </div>
        </div>
      ))}
    </div>
  )

  return (
    <MainLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Trading Strategies</h1>
          <p className="text-gray-600 mt-2">
            Compare and analyze our AI-powered trading strategies with proven track records.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Strategy Selection */}
          <div className="lg:col-span-1">
            <h2 className="text-xl font-semibold mb-4">Available Strategies</h2>
            <div className="space-y-4">
              {loading ? (
                [...Array(4)].map((_, i) => (
                  <Card key={i} className="animate-pulse">
                    <CardContent className="p-6">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                      <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                strategies.map((strategy) => (
                  <StrategyCard
                    key={strategy.id}
                    strategy={strategy}
                    isSelected={selectedStrategy?.id === strategy.id}
                    onClick={() => setSelectedStrategy(strategy)}
                  />
                ))
              )}
            </div>
          </div>

          {/* Strategy Details */}
          <div className="lg:col-span-2">
            {selectedStrategy ? (
              <div className="space-y-6">
                {/* Strategy Header */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                          <selectedStrategy.icon className="h-8 w-8 text-blue-600" />
                        </div>
                        <div>
                          <CardTitle className="text-2xl">{selectedStrategy.name}</CardTitle>
                          <CardDescription className="text-base mt-1">
                            {selectedStrategy.description}
                          </CardDescription>
                        </div>
                      </div>
                      <Button>
                        <Target className="h-4 w-4 mr-2" />
                        Generate Signals
                      </Button>
                    </div>
                  </CardHeader>
                </Card>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Award className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-green-600">{selectedStrategy.successRate}%</p>
                      <p className="text-sm text-gray-600">Success Rate</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4 text-center">
                      <TrendingUp className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-blue-600">{selectedStrategy.avgReturn}%</p>
                      <p className="text-sm text-gray-600">Avg Return</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Clock className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-purple-600">{selectedStrategy.avgHoldingPeriod}M</p>
                      <p className="text-sm text-gray-600">Avg Holding</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Shield className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-orange-600">{selectedStrategy.sharpeRatio}</p>
                      <p className="text-sm text-gray-600">Sharpe Ratio</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Detailed Analysis Tabs */}
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="performance">Performance</TabsTrigger>
                    <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
                    <TabsTrigger value="signals">Recent Signals</TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview" className="space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Strategy Features</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-3">
                          {selectedStrategy.features.map((feature, index) => (
                            <li key={index} className="flex items-start space-x-3">
                              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-700">{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Top Performers</CardTitle>
                        <CardDescription>Best performing stocks from this strategy</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {selectedStrategy.topPerformers.map((performer, index) => (
                            <div key={index} className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                              <div>
                                <p className="font-semibold text-lg">{performer.symbol}</p>
                                <p className="text-sm text-gray-600">{performer.period}</p>
                              </div>
                              <div className="text-right">
                                <p className="text-2xl font-bold text-green-600">+{performer.return}%</p>
                                <Badge variant="secondary" className="text-xs">
                                  {index === 0 ? '🏆 Best' : index === 1 ? '🥈 2nd' : '🥉 3rd'}
                                </Badge>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="performance" className="space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Recent Performance</CardTitle>
                        <CardDescription>Monthly returns over the last 6 months</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <PerformanceChart data={selectedStrategy.recentPerformance} />
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="risk" className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Card>
                        <CardHeader>
                          <CardTitle>Risk Metrics</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div>
                            <div className="flex justify-between mb-2">
                              <span>Max Drawdown</span>
                              <span className="font-semibold">{selectedStrategy.maxDrawdown}%</span>
                            </div>
                            <Progress value={selectedStrategy.maxDrawdown} className="h-2" />
                          </div>
                          
                          <div>
                            <div className="flex justify-between mb-2">
                              <span>Volatility</span>
                              <span className="font-semibold">{selectedStrategy.volatility}%</span>
                            </div>
                            <Progress value={selectedStrategy.volatility} className="h-2" />
                          </div>
                          
                          <div>
                            <div className="flex justify-between mb-2">
                              <span>Win Rate</span>
                              <span className="font-semibold">{selectedStrategy.winRate}%</span>
                            </div>
                            <Progress value={selectedStrategy.winRate} className="h-2" />
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle>Investment Details</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="flex justify-between">
                            <span>Risk Level</span>
                            <Badge className={getRiskColor(selectedStrategy.riskLevel)}>
                              {selectedStrategy.riskLevel}
                            </Badge>
                          </div>
                          <div className="flex justify-between">
                            <span>Min Investment</span>
                            <span className="font-semibold">₹{selectedStrategy.minInvestment.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Timeframe</span>
                            <span className="font-semibold">{selectedStrategy.timeframe}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Active Signals</span>
                            <span className="font-semibold">{selectedStrategy.activeSignals}</span>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  <TabsContent value="signals" className="space-y-6">
                    <Card>
                      <CardContent className="p-12 text-center">
                        <Info className="h-12 w-12 text-blue-500 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Recent Signals</h3>
                        <p className="text-gray-600 mb-4">
                          View recent signals generated by the {selectedStrategy.name} strategy.
                        </p>
                        <Button>
                          <Target className="h-4 w-4 mr-2" />
                          View All Signals
                        </Button>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </div>
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a Strategy</h3>
                  <p className="text-gray-600">Choose a strategy from the left to view detailed analysis.</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
