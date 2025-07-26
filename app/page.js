'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { TrendingUp, TrendingDown, Activity, BarChart3, Settings, RefreshCw, DollarSign, Users } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

export default function EmergentTraderDashboard() {
  const [signals, setSignals] = useState([])
  const [backtestResults, setBacktestResults] = useState(null)
  const [shariahStocks, setShariahStocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('signals')
  const [error, setError] = useState(null)

  // Fetch today's signals
  const fetchTodaysSignals = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/signals/today')
      const data = await response.json()
      
      if (data.success) {
        setSignals(data.data.signals || [])
      } else {
        setError(data.error || 'Failed to fetch signals')
      }
    } catch (err) {
      setError('Network error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Generate new signals
  const generateSignals = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/signals/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy: 'momentum' })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setSignals(data.data.signals || [])
      } else {
        setError(data.error || 'Failed to generate signals')
      }
    } catch (err) {
      setError('Network error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Run backtest
  const runBacktest = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy: 'momentum',
          start_date: '2020-01-01',
          end_date: '2023-12-31'
        })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setBacktestResults(data.data)
      } else {
        setError(data.error || 'Failed to run backtest')
      }
    } catch (err) {
      setError('Network error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Fetch Shariah stocks
  const fetchShariahStocks = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/stocks/shariah')
      const data = await response.json()
      
      if (data.success) {
        setShariahStocks(data.data.stocks || [])
      } else {
        setError(data.error || 'Failed to fetch Shariah stocks')
      }
    } catch (err) {
      setError('Network error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTodaysSignals()
    fetchShariahStocks()
  }, [])

  const mockPerformanceData = [
    { month: 'Jan', portfolio: 100000, benchmark: 100000 },
    { month: 'Feb', portfolio: 102000, benchmark: 101000 },
    { month: 'Mar', portfolio: 98000, benchmark: 99000 },
    { month: 'Apr', portfolio: 105000, benchmark: 103000 },
    { month: 'May', portfolio: 108000, benchmark: 104000 },
    { month: 'Jun', portfolio: 112000, benchmark: 106000 }
  ]

  const sectorData = [
    { name: 'Technology', value: 35, color: '#0088FE' },
    { name: 'Finance', value: 25, color: '#00C49F' },
    { name: 'Healthcare', value: 20, color: '#FFBB28' },
    { name: 'Energy', value: 15, color: '#FF8042' },
    { name: 'Others', value: 5, color: '#8884D8' }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-primary text-primary-foreground p-2 rounded-lg">
                <BarChart3 className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">EmergentTrader</h1>
                <p className="text-muted-foreground">AI-Powered Shariah-Compliant Trading Signals</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button variant="outline" onClick={fetchTodaysSignals} disabled={loading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button onClick={generateSignals} disabled={loading}>
                <Activity className="h-4 w-4 mr-2" />
                Generate Signals
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 border-destructive">
            <AlertDescription className="text-destructive">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active Signals</p>
                  <p className="text-3xl font-bold">{signals.length}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Shariah Stocks</p>
                  <p className="text-3xl font-bold">{shariahStocks.length}</p>
                </div>
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Portfolio Value</p>
                  <p className="text-3xl font-bold">₹1.12L</p>
                </div>
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Win Rate</p>
                  <p className="text-3xl font-bold">68%</p>
                </div>
                <Activity className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="signals">Trading Signals</TabsTrigger>
            <TabsTrigger value="backtest">Backtest Results</TabsTrigger>
            <TabsTrigger value="stocks">Stock Universe</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Trading Signals Tab */}
          <TabsContent value="signals" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Recent Trading Signals</h2>
              <div className="flex space-x-2">
                <Badge variant="outline">Momentum Strategy</Badge>
                <Badge variant="outline">Shariah Compliant</Badge>
              </div>
            </div>

            <div className="grid gap-4">
              {signals.length === 0 ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <Activity className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No signals today</h3>
                    <p className="text-muted-foreground mb-4">
                      Generate new signals to see trading opportunities
                    </p>
                    <Button onClick={generateSignals} disabled={loading}>
                      {loading ? 'Generating...' : 'Generate Signals'}
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                signals.map((signal, index) => (
                  <Card key={index} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="text-lg font-semibold">{signal.symbol}</h3>
                            <Badge 
                              variant={signal.signal_type === 'BUY' ? 'default' : 'destructive'}
                              className={signal.signal_type === 'BUY' ? 'bg-green-100 text-green-800' : ''}
                            >
                              {signal.signal_type}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{signal.sector}</p>
                        </div>
                        
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">Confidence</p>
                          <p className="text-lg font-semibold">
                            {Math.round((signal.confidence_score || 0.8) * 100)}%
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Entry Price</p>
                          <p className="font-semibold">₹{signal.entry_price}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Target</p>
                          <p className="font-semibold text-green-600">₹{signal.target_price}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Stop Loss</p>
                          <p className="font-semibold text-red-600">₹{signal.stop_loss}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Risk:Reward</p>
                          <p className="font-semibold">1:{signal.risk_reward_ratio || 2}</p>
                        </div>
                      </div>

                      <div className="mt-4 flex justify-between items-center">
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <span>RSI: {signal.rsi}</span>
                          <span>Volume: {signal.volume_ratio}x</span>
                          <span>Momentum: {signal.momentum_score}</span>
                        </div>
                        
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            View Details
                          </Button>
                          <Button size="sm">
                            Track Signal
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Backtest Results Tab */}
          <TabsContent value="backtest" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Strategy Backtesting</h2>
              <Button onClick={runBacktest} disabled={loading}>
                {loading ? 'Running...' : 'Run New Backtest'}
              </Button>
            </div>

            {backtestResults ? (
              <div className="grid gap-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="text-center">
                        <p className="text-sm text-muted-foreground">Total Return</p>
                        <p className="text-2xl font-bold text-green-600">
                          {Math.round((backtestResults.performance_metrics?.total_return || 0) * 100)}%
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="text-center">
                        <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                        <p className="text-2xl font-bold">
                          {(backtestResults.performance_metrics?.sharpe_ratio || 0).toFixed(2)}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="text-center">
                        <p className="text-sm text-muted-foreground">Max Drawdown</p>
                        <p className="text-2xl font-bold text-red-600">
                          {Math.round((backtestResults.performance_metrics?.max_drawdown || 0) * 100)}%
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Portfolio Performance</CardTitle>
                    <CardDescription>Historical performance vs benchmark</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={mockPerformanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="portfolio" stroke="#8884d8" strokeWidth={2} />
                        <Line type="monotone" dataKey="benchmark" stroke="#82ca9d" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No backtest results</h3>
                  <p className="text-muted-foreground mb-4">
                    Run a backtest to see historical strategy performance
                  </p>
                  <Button onClick={runBacktest} disabled={loading}>
                    {loading ? 'Running Backtest...' : 'Run Backtest'}
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Stock Universe Tab */}
          <TabsContent value="stocks" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Shariah-Compliant Stock Universe</h2>
              <Badge variant="outline">{shariahStocks.length} stocks</Badge>
            </div>

            <div className="grid gap-4">
              {shariahStocks.map((stock, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="text-lg font-semibold">{stock.symbol}</h3>
                        <p className="text-sm text-muted-foreground">{stock.company_name}</p>
                        <p className="text-sm text-muted-foreground">{stock.sector}</p>
                      </div>
                      
                      <div className="text-right">
                        <p className="text-lg font-semibold">₹{stock.current_price || 'N/A'}</p>
                        <p className="text-sm text-muted-foreground">
                          MCap: ₹{stock.market_cap ? (stock.market_cap / 10000000).toFixed(0) + 'Cr' : 'N/A'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <h2 className="text-xl font-semibold">Portfolio Analytics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Sector Allocation</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={sectorData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        dataKey="value"
                      >
                        {sectorData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Monthly Signal Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={mockPerformanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="portfolio" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}