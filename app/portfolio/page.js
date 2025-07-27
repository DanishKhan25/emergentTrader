'use client'

import { useState } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import usePortfolio from '@/hooks/usePortfolio'
import AddPositionModal from '@/components/portfolio/AddPositionModal'
import FundsManagementModal from '@/components/portfolio/FundsManagementModal'
import PortfolioResetModal from '@/components/portfolio/PortfolioResetModal'
import apiService from '@/lib/api'
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
  RefreshCw,
  Plus,
  Edit,
  Trash2,
  Wallet
} from 'lucide-react'

export default function PortfolioPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [showAddPosition, setShowAddPosition] = useState(false)
  const [showFundsModal, setShowFundsModal] = useState(false)
  const [showResetModal, setShowResetModal] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)
  
  const {
    portfolio,
    positions,
    allocation,
    loading,
    error,
    lastUpdated,
    metrics,
    refreshData,
    isStale
  } = usePortfolio()

  const handleAddPosition = async (positionData) => {
    setActionLoading(true)
    try {
      const response = await fetch('http://localhost:8000/portfolio/positions/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(positionData)
      })
      
      const result = await response.json()
      if (result.success) {
        refreshData() // Refresh portfolio data
        alert(`Position added successfully for ${positionData.symbol}!`)
      } else {
        throw new Error(result.error)
      }
    } catch (err) {
      alert(`Error adding position: ${err.message}`)
      throw err
    } finally {
      setActionLoading(false)
    }
  }

  const handleUpdateFunds = async (fundsData) => {
    setActionLoading(true)
    try {
      const response = await fetch('http://localhost:8000/portfolio/funds/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fundsData)
      })
      
      const result = await response.json()
      if (result.success) {
        refreshData() // Refresh portfolio data
        alert('Funds updated successfully!')
      } else {
        throw new Error(result.error)
      }
    } catch (err) {
      alert(`Error updating funds: ${err.message}`)
      throw err
    } finally {
      setActionLoading(false)
    }
  }

  const handleSellPosition = async (positionId, sellType = 'manual') => {
    const position = positions.find(p => p.id === positionId)
    if (!position) return

    let sellPrice = position.currentPrice
    let reason = 'manual_sell'

    if (sellType === 'target') {
      sellPrice = position.targetPrice
      reason = 'target_hit'
    } else if (sellType === 'sl') {
      sellPrice = position.stopLoss
      reason = 'stop_loss'
    }

    if (!confirm(`Sell ${position.symbol} at ₹${sellPrice}?`)) return

    setActionLoading(true)
    try {
      let response
      if (sellType === 'target') {
        response = await fetch(`http://localhost:8000/positions/${positionId}/target_hit`, {
          method: 'POST'
        })
      } else if (sellType === 'sl') {
        response = await fetch(`http://localhost:8000/positions/${positionId}/stop_loss`, {
          method: 'POST'
        })
      } else {
        response = await fetch(`http://localhost:8000/positions/${positionId}/sell`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            quantity: position.quantity,
            sell_price: sellPrice,
            reason: reason
          })
        })
      }
      
      const result = await response.json()
      if (result.success) {
        refreshData()
        alert(result.message)
      } else {
        throw new Error(result.error)
      }
    } catch (err) {
      alert(`Error selling position: ${err.message}`)
    } finally {
      setActionLoading(false)
    }
  }

  const handleDeletePosition = async (positionId) => {
    if (!confirm('Are you sure you want to delete this position?')) return
    
    setActionLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/portfolio/positions/${positionId}`, {
        method: 'DELETE'
      })
      
      const result = await response.json()
      if (result.success) {
        refreshData()
        alert('Position deleted successfully!')
      } else {
        throw new Error(result.error)
      }
    } catch (err) {
      alert(`Error deleting position: ${err.message}`)
    } finally {
      setActionLoading(false)
    }
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
    switch (strategy?.toLowerCase()) {
      case 'multibagger': return <Target className="h-4 w-4" />
      case 'momentum': return <TrendingUp className="h-4 w-4" />
      case 'swing': return <Activity className="h-4 w-4" />
      case 'breakout': return <Zap className="h-4 w-4" />
      default: return <BarChart3 className="h-4 w-4" />
    }
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

  const formatNumber = (value, decimals = 2) => {
    if (typeof value !== 'number') return '0'
    return value.toFixed(decimals)
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
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold text-lg">{position.symbol}</h3>
                {position.type === 'manual' && (
                  <Badge variant="outline" className="text-xs">Manual</Badge>
                )}
                {position.type === 'signal' && (
                  <Badge variant="outline" className="text-xs bg-green-50 text-green-700">Signal</Badge>
                )}
              </div>
              <p className="text-sm text-gray-600 capitalize">{position.strategy} • {position.quantity} shares</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusBadge(position.status)}
            {position.editable && (
              <div className="flex space-x-1">
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Edit className="h-4 w-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                  onClick={() => handleDeletePosition(position.id)}
                  disabled={actionLoading}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            )}
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
                  {position.pnl >= 0 ? '+' : ''}{formatNumber(position.pnlPercent)}%
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
            <p className="font-semibold">₹{formatNumber(position.avgPrice)}</p>
          </div>
          <div>
            <p className="text-gray-600">Current</p>
            <p className="font-semibold">₹{formatNumber(position.currentPrice)}</p>
          </div>
          <div>
            <p className="text-gray-600">Target</p>
            <p className="font-semibold text-green-600">₹{formatNumber(position.targetPrice)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="h-4 w-4 mr-1" />
            {Math.floor((new Date() - new Date(position.entryDate)) / (1000 * 60 * 60 * 24))} days
          </div>
          <div className="flex space-x-2">
            {position.status === 'active' && (
              <>
                {position.targetPrice && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-green-600 hover:text-green-700"
                    onClick={() => handleSellPosition(position.id, 'target')}
                    disabled={actionLoading}
                  >
                    🎯 Target
                  </Button>
                )}
                {position.stopLoss && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-red-600 hover:text-red-700"
                    onClick={() => handleSellPosition(position.id, 'sl')}
                    disabled={actionLoading}
                  >
                    🛑 SL
                  </Button>
                )}
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleSellPosition(position.id, 'manual')}
                  disabled={actionLoading}
                >
                  Sell
                </Button>
              </>
            )}
            {position.status !== 'active' && (
              <Badge variant="secondary">{position.status.replace('_', ' ')}</Badge>
            )}
            {position.editable && position.status === 'active' && (
              <div className="flex space-x-1">
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Edit className="h-4 w-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                  onClick={() => handleDeletePosition(position.id)}
                  disabled={actionLoading}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </div>

        {position.notes && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-sm text-gray-600">
              <strong>Notes:</strong> {position.notes}
            </p>
          </div>
        )}
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
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </MainLayout>
    )
  }

  if (error) {
    return (
      <MainLayout>
        <div className="p-6">
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Portfolio</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={refreshData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
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
            {lastUpdated && (
              <p className="text-sm text-gray-500 mt-1">
                Last updated: {lastUpdated.toLocaleTimeString()}
                {isStale && <span className="text-orange-500 ml-2">(Data may be stale)</span>}
              </p>
            )}
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => setShowFundsModal(true)}>
              <Wallet className="h-4 w-4 mr-2" />
              Manage Funds
            </Button>
            <Button onClick={() => setShowAddPosition(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Position
            </Button>
            <Button variant="outline" onClick={() => setShowResetModal(true)}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Reset Portfolio
            </Button>
            <Button variant="outline" onClick={refreshData} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>
        </div>

        {/* Funds Summary */}
        {portfolio?.funds && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">Total Funds</p>
                <p className="text-xl font-bold text-blue-600">
                  {formatCurrency(portfolio.funds.total_funds)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Available</p>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(portfolio.funds.available_funds)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Invested</p>
                <p className="text-xl font-bold text-orange-600">
                  {formatCurrency(portfolio.funds.invested_funds)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Value</p>
                  <p className="text-2xl font-bold">{formatCurrency(metrics.totalValue)}</p>
                </div>
                <Briefcase className="h-8 w-8 text-blue-500" />
              </div>
              <div className="mt-2 flex items-center">
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-sm text-green-600 font-medium">
                  +{formatNumber(portfolio?.dayPnLPercent || 0)}% today
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total P&L</p>
                  <p className={`text-2xl font-bold ${metrics.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(metrics.totalPnL)}
                  </p>
                </div>
                {metrics.totalPnL >= 0 ? (
                  <TrendingUp className="h-8 w-8 text-green-500" />
                ) : (
                  <TrendingDown className="h-8 w-8 text-red-500" />
                )}
              </div>
              <div className="mt-2">
                <span className={`text-sm font-medium ${metrics.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {metrics.totalPnL >= 0 ? '+' : ''}{formatNumber(metrics.totalPnLPercent)}% overall
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Positions</p>
                  <p className="text-2xl font-bold">{metrics.activePositionsCount}</p>
                </div>
                <Target className="h-8 w-8 text-purple-500" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  {portfolio?.manualPositions || 0} manual, {portfolio?.signalPositions || 0} signals
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Win Rate</p>
                  <p className="text-2xl font-bold text-green-600">{formatNumber(metrics.winRate)}%</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  {metrics.profitablePositions} profitable, {metrics.losingPositions} losing
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analysis */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 max-w-2xl">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="positions">Positions ({positions.length})</TabsTrigger>
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
                        +{formatNumber(portfolio?.bestPerformer?.return || 0)}%
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
                        {formatNumber(portfolio?.worstPerformer?.return || 0)}%
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
                    <span className="font-bold">{formatNumber(portfolio?.riskMetrics?.sharpeRatio || 0)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Max Drawdown</span>
                    <span className="font-bold text-red-600">{formatNumber(portfolio?.riskMetrics?.maxDrawdown || 0)}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Volatility</span>
                    <span className="font-bold">{formatNumber(portfolio?.riskMetrics?.volatility || 0)}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Beta</span>
                    <span className="font-bold">{formatNumber(portfolio?.riskMetrics?.beta || 0)}</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="positions" className="space-y-6 mt-6">
            {positions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {positions.map((position) => (
                  <PositionCard key={position.id} position={position} />
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No Active Positions</h3>
                  <p className="text-gray-600 mb-4">
                    You don't have any active positions yet. Start by adding a position or generating signals!
                  </p>
                  <div className="flex justify-center space-x-2">
                    <Button onClick={() => setShowAddPosition(true)}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Position
                    </Button>
                    <Button variant="outline">
                      <Target className="h-4 w-4 mr-2" />
                      Generate Signals
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="allocation" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Strategy Allocation</CardTitle>
                  <CardDescription>Portfolio distribution across trading strategies</CardDescription>
                </CardHeader>
                <CardContent>
                  {allocation.length > 0 ? (
                    <AllocationChart data={allocation} />
                  ) : (
                    <div className="text-center py-8">
                      <PieChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No allocation data available</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Allocation Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {allocation.map((item, index) => (
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

        {/* Modals */}
        <AddPositionModal
          isOpen={showAddPosition}
          onClose={() => setShowAddPosition(false)}
          onAdd={handleAddPosition}
          availableFunds={portfolio?.funds?.available_funds || 0}
        />

        <FundsManagementModal
          isOpen={showFundsModal}
          onClose={() => setShowFundsModal(false)}
          onUpdate={handleUpdateFunds}
          funds={portfolio?.funds || { total_funds: 0, available_funds: 0, invested_funds: 0 }}
        />

        <PortfolioResetModal
          isOpen={showResetModal}
          onClose={() => setShowResetModal(false)}
          onReset={refreshData}
        />
      </div>
    </MainLayout>
  )
}
