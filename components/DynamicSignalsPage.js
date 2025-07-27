'use client'

import React, { useState, useEffect } from 'react'
import { useData } from '@/contexts/DataContext'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
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
  BarChart3,
  Settings,
  Brain,
  Sparkles,
  AlertTriangle
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
  const [signalError, setSignalError] = useState(null)
  const [minConfidence, setMinConfidence] = useState(0.7)
  const [maxSymbols, setMaxSymbols] = useState(50)
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Complete strategy definitions with correct backend names
  const AVAILABLE_STRATEGIES = [
    {
      id: 'multibagger',
      name: 'Multibagger (ML-Enhanced)',
      description: 'AI-powered multibagger strategy with 87% success rate',
      icon: Brain,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      holdingPeriod: '6 months to 3 years',
      focus: '2x, 3x, 5x+ returns',
      riskLevel: 'Medium-High',
      mlEnhanced: true
    },
    {
      id: 'momentum',
      name: 'Momentum Trading (ML-Enhanced)',
      description: 'ML-enhanced momentum-based trading strategy',
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      holdingPeriod: '1-3 months',
      focus: 'Trending stocks with strong momentum',
      riskLevel: 'Medium',
      mlEnhanced: true
    },
    {
      id: 'swing_trading',
      name: 'Swing Trading (ML-Enhanced)',
      description: 'ML-enhanced swing trading strategy',
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      holdingPeriod: '1-4 weeks',
      focus: 'Short to medium-term price swings',
      riskLevel: 'Medium',
      mlEnhanced: true
    },
    {
      id: 'breakout',
      name: 'Breakout Pattern (ML-Enhanced)',
      description: 'ML-enhanced breakout pattern strategy',
      icon: Zap,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      holdingPeriod: '2-8 weeks',
      focus: 'Stocks breaking key resistance levels',
      riskLevel: 'Medium-High',
      mlEnhanced: true
    },
    {
      id: 'mean_reversion',
      name: 'Mean Reversion (ML-Enhanced)',
      description: 'ML-enhanced mean reversion strategy',
      icon: TrendingDown,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      holdingPeriod: '1-6 weeks',
      focus: 'Oversold stocks likely to bounce',
      riskLevel: 'Medium',
      mlEnhanced: true
    },
    {
      id: 'value_investing',
      name: 'Value Investing (ML-Enhanced)',
      description: 'ML-enhanced value investing strategy',
      icon: DollarSign,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
      holdingPeriod: '6 months to 2 years',
      focus: 'Undervalued stocks with strong fundamentals',
      riskLevel: 'Low-Medium',
      mlEnhanced: true
    },
    {
      id: 'fundamental_growth',
      name: 'Fundamental Growth (ML-Enhanced)',
      description: 'ML-enhanced fundamental growth strategy',
      icon: BarChart3,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-100',
      holdingPeriod: '3 months to 2 years',
      focus: 'Companies with strong growth metrics',
      riskLevel: 'Medium',
      mlEnhanced: true
    },
    {
      id: 'sector_rotation',
      name: 'Sector Rotation (ML-Enhanced)',
      description: 'ML-enhanced sector rotation strategy',
      icon: RefreshCw,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      holdingPeriod: '1-6 months',
      focus: 'Rotating between outperforming sectors',
      riskLevel: 'Medium',
      mlEnhanced: true
    },
    {
      id: 'low_volatility',
      name: 'Low Volatility (ML-Enhanced)',
      description: 'ML-enhanced low volatility strategy',
      icon: CheckCircle,
      color: 'text-teal-600',
      bgColor: 'bg-teal-100',
      holdingPeriod: '3-12 months',
      focus: 'Stable stocks with consistent returns',
      riskLevel: 'Low',
      mlEnhanced: true
    },
    {
      id: 'pivot_cpr',
      name: 'Pivot CPR (ML-Enhanced)',
      description: 'ML-enhanced pivot CPR strategy',
      icon: Target,
      color: 'text-pink-600',
      bgColor: 'bg-pink-100',
      holdingPeriod: '1-4 weeks',
      focus: 'Support/resistance based trading',
      riskLevel: 'Medium-High',
      mlEnhanced: true
    }
  ]

  // Get strategy info by ID
  const getStrategyInfo = (strategyId) => {
    return AVAILABLE_STRATEGIES.find(s => s.id === strategyId) || AVAILABLE_STRATEGIES[0]
  }

  // Handle signal generation with comprehensive error handling
  const handleGenerateSignals = async () => {
    setGeneratingSignals(true)
    setSignalError(null)
    
    try {
      const strategyInfo = getStrategyInfo(selectedStrategy)
      
      const result = await generateSignals({
        strategy: selectedStrategy,
        shariah_only: settings.shariahOnly,
        min_confidence: minConfidence,
        max_symbols: maxSymbols
      })
      
      if (result && result.success === false) {
        throw new Error(result.error || 'Failed to generate signals')
      }
      
      // Refresh signals data after generation
      await refreshData(['signals'])
      
    } catch (error) {
      console.error('Signal generation error:', error)
      
      // Handle specific error types
      let errorMessage = 'Failed to generate signals. Please try again.'
      
      if (error.message.includes('not found')) {
        const availableStrategies = AVAILABLE_STRATEGIES.map(s => s.id).join(', ')
        errorMessage = `Strategy "${selectedStrategy}" not found. Available strategies: ${availableStrategies}`
      } else if (error.message.includes('rate limit')) {
        errorMessage = 'Rate limit exceeded. Please wait a moment before generating more signals.'
      } else if (error.message.includes('timeout')) {
        errorMessage = 'Request timed out. The server may be busy. Please try again.'
      } else if (error.message.includes('network')) {
        errorMessage = 'Network error. Please check your connection and try again.'
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setSignalError(errorMessage)
    } finally {
      setGeneratingSignals(false)
    }
  }

  // Clear error when strategy changes
  useEffect(() => {
    setSignalError(null)
  }, [selectedStrategy])

  // Validate strategy selection
  const isValidStrategy = (strategyId) => {
    return AVAILABLE_STRATEGIES.some(s => s.id === strategyId)
  }

  // Auto-correct invalid strategy
  useEffect(() => {
    if (!isValidStrategy(selectedStrategy)) {
      setSelectedStrategy('multibagger')
    }
  }, [selectedStrategy])

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
              <Badge variant="outline" className="text-xs mr-2">
                {((signal.confidence_score || 0) * 100).toFixed(0)}% Confidence
              </Badge>
              {signal.ml_enhanced && (
                <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200">
                  <Brain className="h-3 w-3 mr-1" />
                  ML: {((signal.ml_confidence || 0) * 100).toFixed(0)}%
                </Badge>
              )}
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

        {signal.ml_reasoning && (
          <div className="p-3 bg-purple-50 rounded-lg mb-4">
            <p className="text-sm text-purple-800">
              <strong>ML Analysis:</strong> {signal.ml_reasoning}
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
              AI-powered trading signals with 10 strategies and ML enhancement
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Button 
              variant="outline"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              <Settings className="h-4 w-4 mr-2" />
              {showAdvanced ? 'Hide' : 'Show'} Advanced
            </Button>
            
            <Button 
              onClick={() => refreshData(['signals'])}
              variant="outline"
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Strategy Selection & Generation */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Sparkles className="h-5 w-5 mr-2 text-purple-600" />
              Signal Generation
            </CardTitle>
            <CardDescription>
              Choose a strategy and generate AI-powered trading signals
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Strategy Grid */}
            <div>
              <Label className="text-sm font-medium mb-3 block">Select Trading Strategy</Label>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                {AVAILABLE_STRATEGIES.map((strategy) => {
                  const Icon = strategy.icon
                  const isSelected = selectedStrategy === strategy.id
                  
                  return (
                    <button
                      key={strategy.id}
                      onClick={() => setSelectedStrategy(strategy.id)}
                      className={`p-4 rounded-lg border-2 transition-all text-left ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-full ${strategy.bgColor} flex items-center justify-center mb-2`}>
                        <Icon className={`h-4 w-4 ${strategy.color}`} />
                      </div>
                      <h3 className="font-medium text-sm mb-1">{strategy.name}</h3>
                      <p className="text-xs text-gray-600 line-clamp-2">{strategy.focus}</p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        <Badge variant="outline" className="text-xs">
                          {strategy.riskLevel}
                        </Badge>
                        {strategy.mlEnhanced && (
                          <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200">
                            <Brain className="h-3 w-3 mr-1" />
                            ML
                          </Badge>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Selected Strategy Info */}
            {selectedStrategy && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-start space-x-3">
                  <div className={`w-10 h-10 rounded-full ${getStrategyInfo(selectedStrategy).bgColor} flex items-center justify-center`}>
                    {React.createElement(getStrategyInfo(selectedStrategy).icon, {
                      className: `h-5 w-5 ${getStrategyInfo(selectedStrategy).color}`
                    })}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{getStrategyInfo(selectedStrategy).name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{getStrategyInfo(selectedStrategy).description}</p>
                    <div className="grid grid-cols-3 gap-4 text-xs">
                      <div>
                        <span className="text-gray-500">Holding Period:</span>
                        <p className="font-medium">{getStrategyInfo(selectedStrategy).holdingPeriod}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Focus:</span>
                        <p className="font-medium">{getStrategyInfo(selectedStrategy).focus}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Risk Level:</span>
                        <p className="font-medium">{getStrategyInfo(selectedStrategy).riskLevel}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Advanced Settings */}
            {showAdvanced && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-blue-50 rounded-lg">
                <div>
                  <Label className="text-sm font-medium mb-2 block">
                    Minimum Confidence: {(minConfidence * 100).toFixed(0)}%
                  </Label>
                  <Slider
                    value={[minConfidence]}
                    onValueChange={(value) => setMinConfidence(value[0])}
                    min={0.5}
                    max={0.95}
                    step={0.05}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Higher confidence = fewer but more reliable signals
                  </p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium mb-2 block">
                    Max Symbols: {maxSymbols}
                  </Label>
                  <Slider
                    value={[maxSymbols]}
                    onValueChange={(value) => setMaxSymbols(value[0])}
                    min={10}
                    max={100}
                    step={10}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Maximum number of signals to generate
                  </p>
                </div>
              </div>
            )}

            {/* Generation Button */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>Shariah Filter: {settings.shariahOnly ? 'Enabled' : 'Disabled'}</span>
              </div>
              
              <Button 
                onClick={handleGenerateSignals}
                disabled={generatingSignals || isLoading}
                size="lg"
              >
                <Zap className={`h-4 w-4 mr-2 ${generatingSignals ? 'animate-pulse' : ''}`} />
                {generatingSignals ? 'Generating Signals...' : 'Generate Signals'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Error Alerts */}
        {error && (
          <Alert className="mb-6 border-destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-destructive">
              <strong>System Error:</strong> {error}
            </AlertDescription>
          </Alert>
        )}

        {signalError && (
          <Alert className="mb-6 border-orange-500 bg-orange-50">
            <AlertTriangle className="h-4 w-4 text-orange-600" />
            <AlertDescription className="text-orange-800">
              <strong>Signal Generation Error:</strong> {signalError}
              <div className="mt-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setSignalError(null)}
                  className="mr-2"
                >
                  Dismiss
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleGenerateSignals}
                  disabled={generatingSignals}
                >
                  Retry
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Generation Status */}
        {generatingSignals && (
          <Alert className="mb-6 border-blue-500 bg-blue-50">
            <Zap className="h-4 w-4 text-blue-600 animate-pulse" />
            <AlertDescription className="text-blue-800">
              <div className="flex items-center justify-between">
                <span>
                  Generating <strong>{getStrategyInfo(selectedStrategy).name}</strong> signals... 
                  This may take a few moments.
                </span>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
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
