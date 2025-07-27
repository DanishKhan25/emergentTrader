'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  TrendingUp, 
  TrendingDown, 
  Target,
  Shield,
  Clock,
  AlertTriangle,
  CheckCircle,
  Activity,
  Zap,
  RefreshCw,
  ShoppingCart,
  Eye,
  Filter
} from 'lucide-react'

export default function SignalsPage() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showBuyModal, setShowBuyModal] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [selectedSignal, setSelectedSignal] = useState(null)
  const [buyData, setBuyData] = useState({
    quantity: '',
    entry_price: '',
    target_price: '',
    stop_loss: ''
  })
  const [actionLoading, setActionLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [selectedStrategy, setSelectedStrategy] = useState('momentum')

  const strategies = [
    { value: 'momentum', label: 'Momentum', icon: TrendingUp },
    { value: 'multibagger', label: 'Multibagger', icon: Target },
    { value: 'swing', label: 'Swing Trading', icon: Activity },
    { value: 'value_investing', label: 'Value Investing', icon: Shield },
    { value: 'breakout', label: 'Breakout', icon: Zap },
    { value: 'mean_reversion', label: 'Mean Reversion', icon: RefreshCw }
  ]

  useEffect(() => {
    fetchSignals()
  }, [])

  const fetchSignals = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('http://localhost:8000/signals/active')
      const result = await response.json()
      
      if (result.success) {
        setSignals(result.data.signals || [])
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const generateNewSignals = async (strategy = 'momentum') => {
    try {
      setGenerating(true)
      setError(null)
      
      const response = await fetch('http://localhost:8000/signals/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy: strategy,
          symbols: null,
          shariah_only: true,
          min_confidence: 0.6,
          enable_ml: true
        })
      })
      
      const result = await response.json()
      if (result.success) {
        alert(`Generated ${result.data.signals?.length || 0} new signals!`)
        fetchSignals() // Refresh the signals list
      } else {
        throw new Error(result.error)
      }
    } catch (err) {
      setError(`Error generating signals: ${err.message}`)
    } finally {
      setGenerating(false)
    }
  }

  const handleBuySignal = async () => {
    setActionLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/signals/${selectedSignal.id}/buy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...buyData,
          signal_data: selectedSignal
        })
      })
      
      const result = await response.json()
      if (result.success) {
        alert(`Successfully bought ${selectedSignal.symbol}!`)
        setShowBuyModal(false)
        setBuyData({ quantity: '', entry_price: '', target_price: '', stop_loss: '' })
      } else {
        throw new Error(result.error)
      }
    } catch (err) {
      alert(`Error buying signal: ${err.message}`)
    } finally {
      setActionLoading(false)
    }
  }

  const openBuyModal = (signal) => {
    setSelectedSignal(signal)
    const currentPrice = signal.entry_price || signal.price || 0
    setBuyData({
      quantity: '10',
      entry_price: currentPrice.toString(),
      target_price: signal.target_price?.toString() || (currentPrice * 1.2).toFixed(2),
      stop_loss: signal.stop_loss?.toString() || (currentPrice * 0.9).toFixed(2)
    })
    setShowBuyModal(true)
  }

  const handleViewSignal = (signal) => {
    setSelectedSignal(signal)
    setShowDetailsModal(true)
  }

  const getStrategyIcon = (strategy) => {
    switch (strategy?.toLowerCase()) {
      case 'multibagger': return <Target className="h-4 w-4" />
      case 'momentum': return <TrendingUp className="h-4 w-4" />
      case 'swing': return <Activity className="h-4 w-4" />
      case 'breakout': return <Zap className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.8) return <Badge className="bg-green-100 text-green-800">High</Badge>
    if (confidence >= 0.6) return <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>
    return <Badge className="bg-red-100 text-red-800">Low</Badge>
  }

  const formatCurrency = (value) => {
    if (typeof value !== 'number') return '₹0'
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const SignalCard = ({ signal }) => {
    const currentPrice = signal.entry_price || signal.price || 0
    const targetPrice = signal.target_price || 0
    const confidence = signal.confidence || signal.confidence_score || 0
    
    // Calculate upside safely
    const upside = currentPrice > 0 && targetPrice > 0 
      ? ((targetPrice - currentPrice) / currentPrice * 100).toFixed(1)
      : 'N/A'
    
    return (
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                {getStrategyIcon(signal.strategy)}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-lg">{signal.symbol}</h3>
                  <Badge variant="outline" className="text-xs">Signal</Badge>
                </div>
                <p className="text-sm text-gray-600 capitalize">{signal.strategy?.replace('_', ' ')}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {getConfidenceBadge(confidence)}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Entry Price</p>
              <p className="font-semibold">{formatCurrency(currentPrice)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Confidence</p>
              <p className="font-semibold">{(confidence * 100).toFixed(1)}%</p>
            </div>
          </div>

          {targetPrice > 0 && (
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Target</p>
                <p className="font-semibold text-green-600">{formatCurrency(targetPrice)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Upside</p>
                <p className="font-semibold text-green-600">
                  {upside !== 'N/A' ? `${upside}%` : 'N/A'}
                </p>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="h-4 w-4 mr-1" />
              {new Date(signal.generated_at || signal.timestamp).toLocaleDateString()}
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={() => handleViewSignal(signal)}>
                <Eye className="h-4 w-4 mr-1" />
                View
              </Button>
              <Button size="sm" onClick={() => openBuyModal(signal)}>
                <ShoppingCart className="h-4 w-4 mr-1" />
                Buy
              </Button>
            </div>
          </div>

          {signal.sector && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-sm text-gray-600">
                <strong>Sector:</strong> {signal.sector}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="p-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-200 rounded"></div>
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
            <h1 className="text-3xl font-bold text-gray-900">Trading Signals</h1>
            <p className="text-gray-600 mt-2">
              AI-generated trading opportunities. Click "Buy" to convert signals to positions.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select strategy" />
              </SelectTrigger>
              <SelectContent>
                {strategies.map((strategy) => (
                  <SelectItem key={strategy.value} value={strategy.value}>
                    <div className="flex items-center space-x-2">
                      <strategy.icon className="h-4 w-4" />
                      <span>{strategy.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Button 
              onClick={() => generateNewSignals(selectedStrategy)}
              disabled={generating}
            >
              {generating ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Zap className="h-4 w-4 mr-2" />
              )}
              Generate Signals
            </Button>
            
            <Button variant="outline" onClick={fetchSignals} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Signals Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Signals</p>
                  <p className="text-2xl font-bold">{signals.length}</p>
                </div>
                <Activity className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">High Confidence</p>
                  <p className="text-2xl font-bold text-green-600">
                    {signals.filter(s => (s.confidence || s.confidence_score || 0) >= 0.8).length}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Momentum</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {signals.filter(s => s.strategy === 'momentum').length}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Multibagger</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {signals.filter(s => s.strategy === 'multibagger').length}
                  </p>
                </div>
                <Target className="h-8 w-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Signals Grid */}
        {error ? (
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Signals</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={fetchSignals}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        ) : signals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {signals.map((signal, index) => (
              <SignalCard key={signal.id || index} signal={signal} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Signals Available</h2>
            <p className="text-gray-600 mb-6">
              No trading signals found. Generate new signals to get AI-powered trading recommendations.
            </p>
            
            <div className="flex justify-center items-center space-x-4 mb-4">
              <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select strategy" />
                </SelectTrigger>
                <SelectContent>
                  {strategies.map((strategy) => (
                    <SelectItem key={strategy.value} value={strategy.value}>
                      <div className="flex items-center space-x-2">
                        <strategy.icon className="h-4 w-4" />
                        <span>{strategy.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Button 
                onClick={() => generateNewSignals(selectedStrategy)}
                disabled={generating}
                size="lg"
              >
                {generating ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Zap className="h-4 w-4 mr-2" />
                )}
                Generate {strategies.find(s => s.value === selectedStrategy)?.label} Signals
              </Button>
            </div>
          </div>
        )}

        {/* Buy Signal Modal */}
        <Dialog open={showBuyModal} onOpenChange={setShowBuyModal}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Buy Signal: {selectedSignal?.symbol}</DialogTitle>
              <DialogDescription>
                Convert this signal to an actual position in your portfolio
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    type="number"
                    value={buyData.quantity}
                    onChange={(e) => setBuyData(prev => ({ ...prev, quantity: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="entry_price">Entry Price</Label>
                  <Input
                    id="entry_price"
                    type="number"
                    step="0.01"
                    value={buyData.entry_price}
                    onChange={(e) => setBuyData(prev => ({ ...prev, entry_price: e.target.value }))}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="target_price">Target Price (Optional)</Label>
                  <Input
                    id="target_price"
                    type="number"
                    step="0.01"
                    value={buyData.target_price}
                    onChange={(e) => setBuyData(prev => ({ ...prev, target_price: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="stop_loss">Stop Loss (Optional)</Label>
                  <Input
                    id="stop_loss"
                    type="number"
                    step="0.01"
                    value={buyData.stop_loss}
                    onChange={(e) => setBuyData(prev => ({ ...prev, stop_loss: e.target.value }))}
                  />
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-md">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Investment Required:</span>
                  <span className="font-bold text-blue-600">
                    {formatCurrency((parseFloat(buyData.quantity) || 0) * (parseFloat(buyData.entry_price) || 0))}
                  </span>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowBuyModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleBuySignal} disabled={actionLoading}>
                {actionLoading ? 'Buying...' : 'Buy Signal'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        {/* Signal Details Modal */}
        <Dialog open={showDetailsModal} onOpenChange={setShowDetailsModal}>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                {selectedSignal && getStrategyIcon(selectedSignal.strategy)}
                <span>{selectedSignal?.symbol} - Signal Details</span>
              </DialogTitle>
              <DialogDescription>
                Detailed analysis and information about this trading signal
              </DialogDescription>
            </DialogHeader>

            {selectedSignal && (
              <div className="space-y-6">
                {/* Basic Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Symbol</Label>
                      <p className="text-lg font-semibold">{selectedSignal.symbol}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Strategy</Label>
                      <p className="capitalize">{selectedSignal.strategy?.replace('_', ' ')}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Sector</Label>
                      <p>{selectedSignal.sector || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Confidence</Label>
                      <div className="flex items-center space-x-2">
                        <p className="text-lg font-semibold">
                          {((selectedSignal.confidence || selectedSignal.confidence_score || 0) * 100).toFixed(1)}%
                        </p>
                        {getConfidenceBadge(selectedSignal.confidence || selectedSignal.confidence_score || 0)}
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Generated</Label>
                      <p>{new Date(selectedSignal.generated_at || selectedSignal.timestamp).toLocaleString()}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Signal Type</Label>
                      <Badge variant="outline" className="bg-green-50 text-green-700">
                        {selectedSignal.signal_type || 'BUY'}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Price Info */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-3">Price Analysis</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label className="text-sm text-gray-600">Entry Price</Label>
                      <p className="text-lg font-semibold text-blue-600">
                        {formatCurrency(selectedSignal.entry_price || 0)}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm text-gray-600">Target Price</Label>
                      <p className="text-lg font-semibold text-green-600">
                        {formatCurrency(selectedSignal.target_price || 0)}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm text-gray-600">Stop Loss</Label>
                      <p className="text-lg font-semibold text-red-600">
                        {formatCurrency(selectedSignal.stop_loss || 0)}
                      </p>
                    </div>
                  </div>
                  
                  {selectedSignal.entry_price && selectedSignal.target_price && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Potential Upside:</span>
                        <span className="font-semibold text-green-600">
                          {(((selectedSignal.target_price - selectedSignal.entry_price) / selectedSignal.entry_price) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Risk/Reward Ratio:</span>
                        <span className="font-semibold">
                          {selectedSignal.risk_reward_ratio || 'N/A'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Technical Indicators */}
                {(selectedSignal.rsi || selectedSignal.momentum_score || selectedSignal.volume_ratio) && (
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-3">Technical Indicators</h4>
                    <div className="grid grid-cols-3 gap-4">
                      {selectedSignal.rsi && (
                        <div>
                          <Label className="text-sm text-gray-600">RSI</Label>
                          <p className="font-semibold">{selectedSignal.rsi.toFixed(2)}</p>
                        </div>
                      )}
                      {selectedSignal.momentum_score && (
                        <div>
                          <Label className="text-sm text-gray-600">Momentum Score</Label>
                          <p className="font-semibold">{selectedSignal.momentum_score.toFixed(2)}</p>
                        </div>
                      )}
                      {selectedSignal.volume_ratio && (
                        <div>
                          <Label className="text-sm text-gray-600">Volume Ratio</Label>
                          <p className="font-semibold">{selectedSignal.volume_ratio.toFixed(2)}x</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Additional Info */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <Label className="text-gray-600">Market Cap</Label>
                    <p>{selectedSignal.market_cap ? `₹${(selectedSignal.market_cap / 10000000).toFixed(0)} Cr` : 'N/A'}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">Shariah Compliant</Label>
                    <p>{selectedSignal.shariah_compliant ? '✅ Yes' : '❌ No'}</p>
                  </div>
                </div>
              </div>
            )}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowDetailsModal(false)}>
                Close
              </Button>
              <Button onClick={() => {
                setShowDetailsModal(false)
                openBuyModal(selectedSignal)
              }}>
                <ShoppingCart className="h-4 w-4 mr-2" />
                Buy This Signal
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  )
}
