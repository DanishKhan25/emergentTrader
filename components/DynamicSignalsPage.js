'use client'

import { useState, useEffect } from 'react'
import { useData } from '@/contexts/DataContext'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Target,
  Zap,
  TrendingUp,
  TrendingDown,
  Clock,
  DollarSign,
  Percent,
  Activity,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Filter,
  BarChart3
} from 'lucide-react'

export default function DynamicSignalsPage() {
  const {
    todaySignals,
    openSignals,
    signalHistory,
    strategies,
    isLoading,
    error,
    generateSignals,
    refreshData,
    settings
  } = useData()

  const [activeTab, setActiveTab] = useState('today')
  const [selectedStrategy, setSelectedStrategy] = useState('multibagger')
  const [generatingSignals, setGeneratingSignals] = useState(false)
  const [filterStatus, setFilterStatus] = useState('all')
  const [sortBy, setSortBy] = useState('confidence')

  // Handle signal generation
  const handleGenerateSignals = async () => {
    setGeneratingSignals(true)
    try {
      await generateSignals({
        strategy: selectedStrategy,
        shariah_only: settings.shariahOnly,
        min_confidence: 0.7
      })
    } catch (error) {
      console.error('Failed to generate signals:', error)
    } finally {
      setGeneratingSignals(false)
    }
  }

  // Format currency
  const formatCurrency = (value) => {
    if (!value) return '₹0.00'
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(value)
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Get signal status badge
  const getSignalStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return <Badge className="bg-blue-100 text-blue-800">Active</Badge>
      case 'completed':
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>
      case 'stopped':
        return <Badge variant="destructive">Stopped</Badge>
      case 'expired':
        return <Badge variant="secondary">Expired</Badge>
      default:
        return <Badge variant="outline">{status || 'Unknown'}</Badge>
    }
  }

  // Calculate potential return
  const calculateReturn = (entryPrice, targetPrice) => {
    if (!entryPrice || !targetPrice) return 0
    return ((targetPrice - entryPrice) / entryPrice * 100).toFixed(1)
  }

  // Render signal card
  const renderSignalCard = (signal, index) => (
    <Card key={signal.id || index} className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-bold text-lg">{signal.symbol || 'N/A'}</h3>
              <p className="text-sm text-gray-600 capitalize">
                {signal.strategy || 'Unknown'} Strategy
              </p>
              <p className="text-xs text-gray-500">
                {formatDate(signal.generated_at || signal.createdAt)}
              </p>
            </div>
          </div>
          <div className="text-right">
            {getSignalStatusBadge(signal.status)}
            <div className="mt-2">
              <Badge variant="outline" className="text-xs">
                {((signal.confidence_score || 0) * 100).toFixed(0)}% Confidence
              </Badge>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-600">Signal Type</p>
            <div className="flex items-center">
              {signal.signal_type === 'BUY' ? (
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
              )}
              <span className={`font-bold ${
                signal.signal_type === 'BUY' ? 'text-green-600' : 'text-red-600'
              }`}>
                {signal.signal_type || 'N/A'}
              </span>
            </div>
          </div>

          <div>
            <p className="text-xs text-gray-600">Entry Price</p>
            <p className="font-bold">{formatCurrency(signal.entry_price)}</p>
          </div>

          <div>
            <p className="text-xs text-gray-600">Target Price</p>
            <p className="font-bold text-green-600">{formatCurrency(signal.target_price)}</p>
          </div>

          <div>
            <p className="text-xs text-gray-600">Stop Loss</p>
            <p className="font-bold text-red-600">{formatCurrency(signal.stop_loss)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-4">
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <p className="text-xs text-gray-600">Potential Return</p>
              <p className="font-bold text-green-600">
                +{calculateReturn(signal.entry_price, signal.target_price)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-600">Risk</p>
              <p className="font-bold text-red-600">
                -{calculateReturn(signal.entry_price, signal.stop_loss)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-600">R:R Ratio</p>
              <p className="font-bold">
                {signal.target_price && signal.entry_price && signal.stop_loss
                  ? (
                      (signal.target_price - signal.entry_price) /
                      (signal.entry_price - signal.stop_loss)
                    ).toFixed(1)
                  : 'N/A'
                }:1
              </p>
            </div>
          </div>
        </div>

        {signal.reasoning && (
          <div className="p-3 bg-blue-50 rounded-lg mb-4">
            <p className="text-sm text-blue-800">
              <strong>AI Reasoning:</strong> {signal.reasoning}
            </p>
          </div>
        )}

        <div className="flex space-x-2">
          <Button variant="outline" className="flex-1">
            <BarChart3 className="h-4 w-4 mr-2" />
            View Chart
          </Button>
          <Button variant="outline" className="flex-1">
            <Activity className="h-4 w-4 mr-2" />
            Track Signal
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <MainLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Live Trading Signals</h1>
            <p className="text-gray-600 mt-1">
              AI-powered trading signals with real-time generation and tracking
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select Strategy" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="multibagger">Multibagger</SelectItem>
                <SelectItem value="momentum">Momentum</SelectItem>
                <SelectItem value="swing">Swing Trading</SelectItem>
                <SelectItem value="breakout">Breakout</SelectItem>
                <SelectItem value="value">Value Investing</SelectItem>
              </SelectContent>
            </Select>
            
            <Button 
              onClick={() => refreshData(['signals'])}
              variant="outline"
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            
            <Button 
              onClick={handleGenerateSignals}
              disabled={generatingSignals || isLoading}
            >
              <Zap className={`h-4 w-4 mr-2 ${generatingSignals ? 'animate-pulse' : ''}`} />
              {generatingSignals ? 'Generating...' : 'Generate Signals'}
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 border-destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-destructive">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Generation Status */}
        {generatingSignals && (
          <Alert className="mb-6 border-blue-500 bg-blue-50">
            <Zap className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800">
              Generating new {selectedStrategy} signals... This may take a few moments.
            </AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6 text-center">
              <Target className="h-8 w-8 text-blue-500 mx-auto mb-2" />
              <p className="text-2xl font-bold">{todaySignals.length}</p>
              <p className="text-sm text-gray-600">Today's Signals</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6 text-center">
              <Activity className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <p className="text-2xl font-bold">{openSignals.length}</p>
              <p className="text-sm text-gray-600">Open Positions</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6 text-center">
              <CheckCircle className="h-8 w-8 text-purple-500 mx-auto mb-2" />
              <p className="text-2xl font-bold">87%</p>
              <p className="text-sm text-gray-600">Success Rate</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6 text-center">
              <TrendingUp className="h-8 w-8 text-orange-500 mx-auto mb-2" />
              <p className="text-2xl font-bold">34.7%</p>
              <p className="text-sm text-gray-600">Avg Return</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="today">Today ({todaySignals.length})</TabsTrigger>
            <TabsTrigger value="open">Open ({openSignals.length})</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>

          {/* Today's Signals */}
          <TabsContent value="today" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Today's Signals</span>
                  <Badge variant="outline" className="animate-pulse">
                    Live
                  </Badge>
                </CardTitle>
                <CardDescription>
                  Real-time signals generated today using AI analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                ) : todaySignals.length > 0 ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {todaySignals.map(renderSignalCard)}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      No signals generated today
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Generate new signals using our AI-powered analysis engine
                    </p>
                    <Button onClick={handleGenerateSignals} disabled={generatingSignals}>
                      <Zap className="h-4 w-4 mr-2" />
                      Generate New Signals
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Open Signals */}
          <TabsContent value="open" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Open Positions</CardTitle>
                <CardDescription>
                  Currently active trading positions being tracked
                </CardDescription>
              </CardHeader>
              <CardContent>
                {openSignals.length > 0 ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {openSignals.map(renderSignalCard)}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Activity className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      No open positions
                    </h3>
                    <p className="text-gray-600">
                      Generate signals and start tracking positions
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Signal History */}
          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Signal History</CardTitle>
                <CardDescription>
                  Historical performance of generated signals
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Clock className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Signal history coming soon
                  </h3>
                  <p className="text-gray-600">
                    Historical signal performance and analytics will be available here
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
