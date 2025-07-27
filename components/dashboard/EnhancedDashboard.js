'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TrendingUp, 
  Target, 
  Zap, 
  Activity, 
  BarChart3, 
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Clock,
  Settings,
  Eye,
  Download,
  Filter
} from 'lucide-react'

export default function EnhancedDashboard() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [generationResults, setGenerationResults] = useState(null)
  const [marketRegime, setMarketRegime] = useState(null)
  const [portfolioData, setPortfolioData] = useState(null)
  const [logLevel, setLogLevel] = useState('INFO')
  const [recentLogs, setRecentLogs] = useState([])

  useEffect(() => {
    loadDashboardData()
    loadMarketRegime()
    loadLogLevel()
  }, [])

  const loadDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:8000/portfolio')
      const data = await response.json()
      if (data.success) {
        setPortfolioData(data.data)
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    }
  }

  const loadMarketRegime = async () => {
    try {
      const response = await fetch('http://localhost:8000/market-regime/summary')
      const data = await response.json()
      if (data.success) {
        setMarketRegime(data.data)
      }
    } catch (error) {
      console.error('Error loading market regime:', error)
    }
  }

  const loadLogLevel = async () => {
    try {
      const response = await fetch('http://localhost:8000/logging/status')
      const data = await response.json()
      if (data.success) {
        setLogLevel(data.data.current_level)
      }
    } catch (error) {
      console.error('Error loading log level:', error)
    }
  }

  const generateAllSignals = async () => {
    setIsGenerating(true)
    setGenerationProgress(0)
    setGenerationResults(null)

    try {
      // Get all available strategies
      const strategiesResponse = await fetch('http://localhost:8000/strategies')
      const strategiesData = await strategiesResponse.json()
      
      if (!strategiesData.success) {
        throw new Error('Failed to fetch strategies')
      }

      const strategies = strategiesData.data || []
      const totalStrategies = strategies.length
      let completedStrategies = 0
      const allResults = []

      // Generate signals for each strategy
      for (const strategy of strategies) {
        try {
          setGenerationProgress((completedStrategies / totalStrategies) * 100)
          
          const response = await fetch('http://localhost:8000/signals/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              strategy: strategy.name || strategy,
              symbols: null, // Generate for all stocks
              shariah_only: true,
              min_confidence: 0.7
            })
          })

          const result = await response.json()
          
          if (result.success && result.data) {
            allResults.push({
              strategy: strategy.name || strategy,
              signals: result.data,
              count: result.data.length,
              success: true
            })
          } else {
            allResults.push({
              strategy: strategy.name || strategy,
              signals: [],
              count: 0,
              success: false,
              error: result.error
            })
          }
        } catch (error) {
          allResults.push({
            strategy: strategy.name || strategy,
            signals: [],
            count: 0,
            success: false,
            error: error.message
          })
        }

        completedStrategies++
      }

      setGenerationProgress(100)
      
      // Compile final results
      const totalSignals = allResults.reduce((sum, result) => sum + result.count, 0)
      const successfulStrategies = allResults.filter(r => r.success).length
      const highConfidenceSignals = allResults
        .flatMap(r => r.signals)
        .filter(s => s.confidence >= 0.85).length

      setGenerationResults({
        totalStrategies: totalStrategies,
        successfulStrategies: successfulStrategies,
        totalSignals: totalSignals,
        highConfidenceSignals: highConfidenceSignals,
        results: allResults,
        timestamp: new Date().toISOString()
      })

    } catch (error) {
      console.error('Error generating signals:', error)
      setGenerationResults({
        error: error.message,
        timestamp: new Date().toISOString()
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const changeLogLevel = async (newLevel) => {
    try {
      const response = await fetch('http://localhost:8000/logging/level', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level: newLevel })
      })

      const data = await response.json()
      if (data.success) {
        setLogLevel(newLevel)
      }
    } catch (error) {
      console.error('Error changing log level:', error)
    }
  }

  const viewLogs = async (component = 'main') => {
    try {
      const response = await fetch(`http://localhost:8000/logging/recent/${component}?lines=50`)
      const data = await response.json()
      if (data.success) {
        setRecentLogs(data.data.logs)
      }
    } catch (error) {
      console.error('Error loading logs:', error)
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Enhanced Trading Dashboard</h1>
          <p className="text-gray-600 mt-1">Comprehensive signal generation and market analysis</p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={loadDashboardData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Market Regime Status */}
      {marketRegime && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Market Regime Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Badge className={getRegimeColor(marketRegime.current_regime)}>
                  {marketRegime.current_regime.toUpperCase()}
                </Badge>
                <div className="text-sm text-gray-600">
                  Confidence: {(marketRegime.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-sm text-gray-500">
                {marketRegime.description}
              </div>
            </div>
            
            {marketRegime.strategy_recommendations && (
              <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="font-medium text-green-600">Recommended</div>
                  <div className="text-gray-600">
                    {marketRegime.strategy_recommendations.use?.join(', ') || 'None'}
                  </div>
                </div>
                <div>
                  <div className="font-medium text-yellow-600">Use Caution</div>
                  <div className="text-gray-600">
                    {marketRegime.strategy_recommendations.caution?.join(', ') || 'None'}
                  </div>
                </div>
                <div>
                  <div className="font-medium text-red-600">Avoid</div>
                  <div className="text-gray-600">
                    {marketRegime.strategy_recommendations.avoid?.join(', ') || 'None'}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Generate All Signals Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Multi-Strategy Signal Generation
          </CardTitle>
          <CardDescription>
            Generate trading signals using all available strategies across all stocks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Button 
              onClick={generateAllSignals} 
              disabled={isGenerating}
              size="lg"
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Generating Signals...
                </>
              ) : (
                <>
                  <Target className="h-4 w-4 mr-2" />
                  Generate All Signals
                </>
              )}
            </Button>
            
            {isGenerating && (
              <div className="flex-1">
                <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{generationProgress.toFixed(0)}%</span>
                </div>
                <Progress value={generationProgress} className="h-2" />
              </div>
            )}
          </div>

          {/* Generation Results */}
          {generationResults && (
            <div className="mt-6">
              {generationResults.error ? (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Signal generation failed: {generationResults.error}
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-4">
                  <Alert>
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription>
                      Successfully generated {generationResults.totalSignals} signals 
                      from {generationResults.successfulStrategies}/{generationResults.totalStrategies} strategies
                    </AlertDescription>
                  </Alert>

                  {/* Results Summary */}
                  <div className="grid grid-cols-4 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {generationResults.totalSignals}
                          </div>
                          <div className="text-sm text-gray-600">Total Signals</div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {generationResults.highConfidenceSignals}
                          </div>
                          <div className="text-sm text-gray-600">High Confidence</div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">
                            {generationResults.successfulStrategies}
                          </div>
                          <div className="text-sm text-gray-600">Strategies Used</div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-600">
                            {new Set(generationResults.results.flatMap(r => r.signals.map(s => s.symbol))).size}
                          </div>
                          <div className="text-sm text-gray-600">Unique Stocks</div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Strategy Breakdown */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Strategy Breakdown</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {generationResults.results.map((result, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className={`w-3 h-3 rounded-full ${result.success ? 'bg-green-500' : 'bg-red-500'}`} />
                              <span className="font-medium">{result.strategy}</span>
                            </div>
                            <div className="flex items-center gap-4">
                              <span className="text-sm text-gray-600">
                                {result.count} signals
                              </span>
                              {!result.success && (
                                <span className="text-xs text-red-600">
                                  {result.error}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Logging Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Logging Control Panel
          </CardTitle>
          <CardDescription>
            Monitor system logs and adjust logging levels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Log Level:</span>
              <Badge variant="outline">{logLevel}</Badge>
            </div>
            
            <div className="flex gap-2">
              {['DEBUG', 'INFO', 'WARNING', 'ERROR'].map((level) => (
                <Button
                  key={level}
                  variant={logLevel === level ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => changeLogLevel(level)}
                >
                  {level}
                </Button>
              ))}
            </div>
            
            <Button onClick={() => viewLogs('main')} variant="outline" size="sm">
              <Eye className="h-4 w-4 mr-2" />
              View Logs
            </Button>
          </div>

          {recentLogs.length > 0 && (
            <div className="mt-4">
              <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-xs max-h-64 overflow-y-auto">
                {recentLogs.slice(-20).map((log, index) => (
                  <div key={index} className="mb-1">
                    {log}
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Portfolio Overview */}
      {portfolioData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Portfolio Value
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ₹{portfolioData.totalValue?.toLocaleString() || '0'}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Available: ₹{portfolioData.availableFunds?.toLocaleString() || '0'}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Active Positions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {portfolioData.activePositions || 0}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Total positions held
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Today's P&L
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${
                (portfolioData.todayPnL || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ₹{portfolioData.todayPnL?.toLocaleString() || '0'}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {((portfolioData.todayPnL || 0) / (portfolioData.totalValue || 1) * 100).toFixed(2)}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <Target className="h-6 w-6" />
              <span className="text-sm">View Signals</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <BarChart3 className="h-6 w-6" />
              <span className="text-sm">Portfolio</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <TrendingUp className="h-6 w-6" />
              <span className="text-sm">Analytics</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <Settings className="h-6 w-6" />
              <span className="text-sm">Settings</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
