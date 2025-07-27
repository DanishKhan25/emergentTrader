'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Zap,
  Target,
  Clock,
  RefreshCw,
  Calendar,
  PieChart,
  LineChart
} from 'lucide-react'

export default function MarketRegimeAnalytics() {
  const [currentRegime, setCurrentRegime] = useState(null)
  const [regimeHistory, setRegimeHistory] = useState([])
  const [strategyPerformance, setStrategyPerformance] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadRegimeAnalytics()
  }, [])

  const loadRegimeAnalytics = async () => {
    setLoading(true)
    try {
      // Get current regime
      const regimeResponse = await fetch('http://localhost:8000/market-regime/summary')
      const regimeData = await regimeResponse.json()
      
      if (regimeData.success) {
        setCurrentRegime(regimeData.data)
      }

      // Simulate regime history (in production, this would come from your backend)
      const simulatedHistory = generateRegimeHistory()
      setRegimeHistory(simulatedHistory)

      // Simulate strategy performance by regime
      const simulatedPerformance = generateStrategyPerformance()
      setStrategyPerformance(simulatedPerformance)

    } catch (error) {
      console.error('Error loading regime analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateRegimeHistory = () => {
    // Simulate 30 days of regime history
    const regimes = ['bull', 'bear', 'sideways', 'volatile']
    const history = []
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      
      // Simulate regime changes with some persistence
      const prevRegime = history.length > 0 ? history[history.length - 1].regime : 'sideways'
      let regime = prevRegime
      
      // 20% chance of regime change
      if (Math.random() < 0.2) {
        regime = regimes[Math.floor(Math.random() * regimes.length)]
      }
      
      history.push({
        date: date.toISOString().split('T')[0],
        regime,
        confidence: 0.5 + Math.random() * 0.4 // 50-90% confidence
      })
    }
    
    return history
  }

  const generateStrategyPerformance = () => {
    const strategies = ['multibagger', 'momentum', 'swing', 'breakout', 'mean_reversion', 'value']
    const regimes = ['bull', 'bear', 'sideways', 'volatile']
    const performance = {}
    
    strategies.forEach(strategy => {
      performance[strategy] = {}
      regimes.forEach(regime => {
        // Simulate performance based on strategy-regime compatibility
        const basePerformance = Math.random() * 20 - 10 // -10% to +10%
        let multiplier = 1
        
        // Apply realistic multipliers based on strategy-regime fit
        if (strategy === 'multibagger' && regime === 'bull') multiplier = 1.5
        if (strategy === 'momentum' && regime === 'bull') multiplier = 1.3
        if (strategy === 'swing' && regime === 'sideways') multiplier = 1.4
        if (strategy === 'breakout' && regime === 'volatile') multiplier = 1.6
        if (strategy === 'mean_reversion' && regime === 'sideways') multiplier = 1.3
        if (strategy === 'value' && regime === 'bear') multiplier = 1.2
        
        performance[strategy][regime] = {
          return: basePerformance * multiplier,
          trades: Math.floor(Math.random() * 50) + 10,
          winRate: 0.4 + Math.random() * 0.4, // 40-80% win rate
          avgReturn: basePerformance * multiplier * 0.1
        }
      })
    })
    
    return performance
  }

  const getRegimeIcon = (regime) => {
    switch (regime) {
      case 'bull': return <TrendingUp className="h-4 w-4" />
      case 'bear': return <TrendingDown className="h-4 w-4" />
      case 'sideways': return <BarChart3 className="h-4 w-4" />
      case 'volatile': return <Zap className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  const getRegimeColor = (regime) => {
    const colors = {
      bull: 'text-green-600 bg-green-50 border-green-200',
      bear: 'text-red-600 bg-red-50 border-red-200',
      sideways: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      volatile: 'text-purple-600 bg-purple-50 border-purple-200',
      unknown: 'text-gray-600 bg-gray-50 border-gray-200'
    }
    return colors[regime] || colors.unknown
  }

  const getRegimeDistribution = () => {
    const distribution = regimeHistory.reduce((acc, day) => {
      acc[day.regime] = (acc[day.regime] || 0) + 1
      return acc
    }, {})
    
    const total = regimeHistory.length
    return Object.entries(distribution).map(([regime, count]) => ({
      regime,
      count,
      percentage: (count / total) * 100
    }))
  }

  const getBestStrategiesForRegime = (regime) => {
    if (!strategyPerformance || !regime) return []
    
    return Object.entries(strategyPerformance)
      .map(([strategy, regimeData]) => ({
        strategy,
        performance: regimeData[regime] || { return: 0, winRate: 0 }
      }))
      .sort((a, b) => b.performance.return - a.performance.return)
      .slice(0, 3)
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin mr-2" />
            <span>Loading market regime analytics...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  const regimeDistribution = getRegimeDistribution()

  return (
    <div className="space-y-6">
      {/* Current Regime Overview */}
      {currentRegime && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getRegimeIcon(currentRegime.current_regime)}
              Current Market Regime
            </CardTitle>
            <CardDescription>
              Real-time market condition analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <Badge className={getRegimeColor(currentRegime.current_regime)}>
                  {currentRegime.current_regime.toUpperCase()}
                </Badge>
                <div className="text-sm text-gray-600">
                  Confidence: {(currentRegime.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <Button onClick={loadRegimeAnalytics} variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
            
            <p className="text-sm text-gray-600 mb-4">
              {currentRegime.description}
            </p>

            {/* Best strategies for current regime */}
            <div>
              <h4 className="font-medium mb-3">Top Strategies for Current Regime</h4>
              <div className="grid grid-cols-3 gap-4">
                {getBestStrategiesForRegime(currentRegime.current_regime).map((item, index) => (
                  <div key={item.strategy} className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">#{index + 1}</div>
                    <div className="text-sm font-medium capitalize">{item.strategy}</div>
                    <div className="text-xs text-gray-600">
                      {item.performance.return > 0 ? '+' : ''}{item.performance.return.toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="distribution" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="distribution">Regime Distribution</TabsTrigger>
          <TabsTrigger value="performance">Strategy Performance</TabsTrigger>
          <TabsTrigger value="history">Historical Analysis</TabsTrigger>
        </TabsList>

        {/* Regime Distribution Tab */}
        <TabsContent value="distribution" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5" />
                Market Regime Distribution (Last 30 Days)
              </CardTitle>
              <CardDescription>
                How market conditions have been distributed over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {regimeDistribution.map((item) => (
                  <div key={item.regime} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getRegimeIcon(item.regime)}
                      <span className="font-medium capitalize">{item.regime}</span>
                    </div>
                    <div className="flex items-center gap-4 flex-1 ml-4">
                      <Progress value={item.percentage} className="flex-1" />
                      <div className="text-sm text-gray-600 w-16 text-right">
                        {item.percentage.toFixed(0)}%
                      </div>
                      <div className="text-sm text-gray-500 w-12 text-right">
                        {item.count}d
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Strategy Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Strategy Performance by Market Regime
              </CardTitle>
              <CardDescription>
                How different strategies perform in various market conditions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Strategy</th>
                      <th className="text-center p-2">Bull</th>
                      <th className="text-center p-2">Bear</th>
                      <th className="text-center p-2">Sideways</th>
                      <th className="text-center p-2">Volatile</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(strategyPerformance).map(([strategy, regimeData]) => (
                      <tr key={strategy} className="border-b">
                        <td className="p-2 font-medium capitalize">{strategy}</td>
                        {['bull', 'bear', 'sideways', 'volatile'].map((regime) => {
                          const data = regimeData[regime] || { return: 0, winRate: 0 }
                          return (
                            <td key={regime} className="p-2 text-center">
                              <div className={`font-medium ${
                                data.return > 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {data.return > 0 ? '+' : ''}{data.return.toFixed(1)}%
                              </div>
                              <div className="text-xs text-gray-500">
                                {(data.winRate * 100).toFixed(0)}% win
                              </div>
                            </td>
                          )
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Historical Analysis Tab */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="h-5 w-5" />
                Regime History Timeline
              </CardTitle>
              <CardDescription>
                Market regime changes over the last 30 days
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {regimeHistory.slice().reverse().map((day, index) => (
                  <div key={day.date} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                    <div className="flex items-center gap-3">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <span className="text-sm">{new Date(day.date).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge className={getRegimeColor(day.regime)} variant="outline">
                        {day.regime.toUpperCase()}
                      </Badge>
                      <span className="text-sm text-gray-600 w-12 text-right">
                        {(day.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Regime Transition Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Regime Insights</CardTitle>
              <CardDescription>
                Key insights from recent market regime analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Most Stable Regime</h4>
                  <div className="flex items-center gap-2">
                    {getRegimeIcon(regimeDistribution[0]?.regime)}
                    <span className="capitalize">{regimeDistribution[0]?.regime}</span>
                    <Badge variant="outline">
                      {regimeDistribution[0]?.percentage.toFixed(0)}% of time
                    </Badge>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-3">Average Confidence</h4>
                  <div className="text-2xl font-bold text-blue-600">
                    {(regimeHistory.reduce((sum, day) => sum + day.confidence, 0) / regimeHistory.length * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
