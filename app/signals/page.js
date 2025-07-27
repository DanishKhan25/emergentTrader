'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Target, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  BarChart3
} from 'lucide-react'

export default function SignalsPage() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedStrategy, setSelectedStrategy] = useState('multibagger')

  // Mock signals data
  const mockSignals = [
    {
      id: 1,
      symbol: 'RELIANCE',
      strategy: 'multibagger',
      signalType: 'BUY',
      entryPrice: 2456.75,
      targetPrice: 4913.50,
      stopLoss: 1965.40,
      confidence: 0.87,
      generatedAt: '2025-01-27T09:15:00Z',
      status: 'active',
      currentPrice: 2478.30,
      returns: 0.88,
      timeframe: '6-12 months'
    },
    {
      id: 2,
      symbol: 'TCS',
      strategy: 'momentum',
      signalType: 'BUY',
      entryPrice: 3789.20,
      targetPrice: 4167.12,
      stopLoss: 3410.28,
      confidence: 0.73,
      generatedAt: '2025-01-27T09:15:00Z',
      status: 'active',
      currentPrice: 3801.45,
      returns: 0.32,
      timeframe: '1-3 months'
    },
    {
      id: 3,
      symbol: 'INFY',
      strategy: 'swing',
      signalType: 'BUY',
      entryPrice: 1456.30,
      targetPrice: 1602.93,
      stopLoss: 1310.67,
      confidence: 0.68,
      generatedAt: '2025-01-27T09:15:00Z',
      status: 'target_hit',
      currentPrice: 1612.45,
      returns: 10.72,
      timeframe: '2-6 weeks'
    },
    {
      id: 4,
      symbol: 'WIPRO',
      strategy: 'multibagger',
      signalType: 'BUY',
      entryPrice: 445.60,
      targetPrice: 891.20,
      stopLoss: 356.48,
      confidence: 0.82,
      generatedAt: '2025-01-26T09:15:00Z',
      status: 'active',
      currentPrice: 467.80,
      returns: 4.98,
      timeframe: '6-18 months'
    }
  ]

  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setSignals(mockSignals)
      setLoading(false)
    }, 1000)
  }, [])

  const generateNewSignals = async () => {
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      setLoading(false)
    }, 2000)
  }

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
      case 'multibagger':
        return <Target className="h-4 w-4" />
      case 'momentum':
        return <TrendingUp className="h-4 w-4" />
      case 'swing':
        return <Activity className="h-4 w-4" />
      default:
        return <BarChart3 className="h-4 w-4" />
    }
  }

  const SignalCard = ({ signal }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              {getStrategyIcon(signal.strategy)}
            </div>
            <div>
              <h3 className="font-semibold text-lg">{signal.symbol}</h3>
              <p className="text-sm text-gray-600 capitalize">{signal.strategy} Strategy</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusBadge(signal.status)}
            <Badge variant="outline" className="text-xs">
              {(signal.confidence * 100).toFixed(0)}% Confidence
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600">Entry Price</p>
            <p className="font-semibold">₹{signal.entryPrice.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Target Price</p>
            <p className="font-semibold text-green-600">₹{signal.targetPrice.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Stop Loss</p>
            <p className="font-semibold text-red-600">₹{signal.stopLoss.toFixed(2)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-gray-600">Current Price</p>
            <div className="flex items-center space-x-2">
              <p className="font-semibold">₹{signal.currentPrice.toFixed(2)}</p>
              <div className="flex items-center">
                {signal.returns >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-sm font-medium ml-1 ${
                  signal.returns >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {signal.returns >= 0 ? '+' : ''}{signal.returns.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Timeframe</p>
            <p className="font-semibold">{signal.timeframe}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="h-4 w-4 mr-1" />
            {new Date(signal.generatedAt).toLocaleDateString()}
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              View Chart
            </Button>
            <Button size="sm">
              Track
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const strategies = [
    { value: 'multibagger', label: 'Multibagger (87% Success)', icon: Target },
    { value: 'momentum', label: 'Momentum Trading', icon: TrendingUp },
    { value: 'swing', label: 'Swing Trading', icon: Activity },
    { value: 'breakout', label: 'Breakout Strategy', icon: Zap },
  ]

  return (
    <MainLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Trading Signals</h1>
          <p className="text-gray-600 mt-2">
            AI-powered trading signals with proven 87% success rate on multibagger predictions.
          </p>
        </div>

        {/* Signal Generation */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Zap className="h-5 w-5 mr-2" />
              Generate New Signals
            </CardTitle>
            <CardDescription>
              Select a strategy and generate fresh trading signals based on current market conditions.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select strategy" />
                  </SelectTrigger>
                  <SelectContent>
                    {strategies.map((strategy) => (
                      <SelectItem key={strategy.value} value={strategy.value}>
                        <div className="flex items-center">
                          <strategy.icon className="h-4 w-4 mr-2" />
                          {strategy.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={generateNewSignals} disabled={loading} className="sm:w-auto">
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <Target className="h-4 w-4 mr-2" />
                    Generate Signals
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Signals Tabs */}
        <Tabs defaultValue="all" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 max-w-2xl">
            <TabsTrigger value="all">All Signals ({signals.length})</TabsTrigger>
            <TabsTrigger value="active">Active ({signals.filter(s => s.status === 'active').length})</TabsTrigger>
            <TabsTrigger value="completed">Completed ({signals.filter(s => s.status === 'target_hit').length})</TabsTrigger>
            <TabsTrigger value="stopped">Stopped ({signals.filter(s => s.status === 'stop_loss').length})</TabsTrigger>
          </TabsList>

          <TabsContent value="all">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[...Array(4)].map((_, i) => (
                  <Card key={i} className="animate-pulse">
                    <CardContent className="p-6">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                      <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {signals.map((signal) => (
                  <SignalCard key={signal.id} signal={signal} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="active">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {signals.filter(s => s.status === 'active').map((signal) => (
                <SignalCard key={signal.id} signal={signal} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="completed">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {signals.filter(s => s.status === 'target_hit').map((signal) => (
                <SignalCard key={signal.id} signal={signal} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="stopped">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {signals.filter(s => s.status === 'stop_loss').map((signal) => (
                <SignalCard key={signal.id} signal={signal} />
              ))}
            </div>
            {signals.filter(s => s.status === 'stop_loss').length === 0 && (
              <Card>
                <CardContent className="p-12 text-center">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No stopped signals</h3>
                  <p className="text-gray-600">Great! None of your signals have hit stop loss.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
