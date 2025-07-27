'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Zap,
  CheckCircle,
  AlertTriangle,
  Clock,
  RefreshCw
} from 'lucide-react'

export default function MarketRegimeFilter({ onRegimeChange, onStrategyFilter }) {
  const [marketRegime, setMarketRegime] = useState(null)
  const [filteredStrategies, setFilteredStrategies] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadMarketRegime()
  }, [])

  const loadMarketRegime = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/market-regime/summary')
      const data = await response.json()
      
      if (data.success) {
        setMarketRegime(data.data)
        onRegimeChange?.(data.data)
        
        // Auto-filter strategies based on regime
        await filterStrategiesForRegime()
      }
    } catch (error) {
      console.error('Error loading market regime:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterStrategiesForRegime = async () => {
    try {
      const strategies = ['multibagger', 'momentum', 'swing', 'breakout', 'mean_reversion', 'value']
      
      const response = await fetch('http://localhost:8000/market-regime/filter-strategies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategies })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setFilteredStrategies(data.data)
        onStrategyFilter?.(data.data)
      }
    } catch (error) {
      console.error('Error filtering strategies:', error)
    }
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

  const getStrategyStatusIcon = (category) => {
    switch (category) {
      case 'excellent':
      case 'good':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'moderate':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'poor':
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      default:
        return <Activity className="h-4 w-4 text-gray-600" />
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin mr-2" />
            <span>Loading market regime...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!marketRegime) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Unable to load market regime data. Some features may be limited.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-4">
      {/* Market Regime Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getRegimeIcon(marketRegime.current_regime)}
            Current Market Regime
          </CardTitle>
          <CardDescription>
            Market analysis for optimal strategy selection
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Badge className={getRegimeColor(marketRegime.current_regime)}>
                {marketRegime.current_regime.toUpperCase()}
              </Badge>
              <div className="text-sm text-gray-600">
                Confidence: {(marketRegime.confidence * 100).toFixed(1)}%
              </div>
            </div>
            <Button onClick={loadMarketRegime} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
          
          <p className="text-sm text-gray-600 mb-4">
            {marketRegime.description}
          </p>

          {marketRegime.last_update && (
            <p className="text-xs text-gray-400">
              Last updated: {new Date(marketRegime.last_update).toLocaleString()}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Strategy Recommendations */}
      {filteredStrategies && (
        <Card>
          <CardHeader>
            <CardTitle>Strategy Recommendations</CardTitle>
            <CardDescription>
              Strategies optimized for current market conditions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Recommended Strategies */}
              {filteredStrategies.recommendations.use.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="font-medium text-green-600">Recommended</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {filteredStrategies.recommendations.use.map((strategy) => (
                      <Badge key={strategy} variant="outline" className="text-green-600 border-green-200">
                        {strategy}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Caution Strategies */}
              {filteredStrategies.recommendations.caution.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 text-yellow-600" />
                    <span className="font-medium text-yellow-600">Use with Caution</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {filteredStrategies.recommendations.caution.map((strategy) => (
                      <Badge key={strategy} variant="outline" className="text-yellow-600 border-yellow-200">
                        {strategy}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Avoid Strategies */}
              {filteredStrategies.recommendations.avoid.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <span className="font-medium text-red-600">Not Recommended</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {filteredStrategies.recommendations.avoid.map((strategy) => (
                      <Badge key={strategy} variant="outline" className="text-red-600 border-red-200">
                        {strategy}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Strategy Scores */}
            <div className="mt-6">
              <h4 className="font-medium mb-3">Strategy Compatibility Scores</h4>
              <div className="space-y-2">
                {Object.entries(filteredStrategies.strategy_scores).map(([strategy, score]) => (
                  <div key={strategy} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getStrategyStatusIcon(
                        score >= 0.8 ? 'excellent' : 
                        score >= 0.6 ? 'good' : 
                        score >= 0.4 ? 'moderate' : 'poor'
                      )}
                      <span className="text-sm font-medium capitalize">{strategy}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            score >= 0.8 ? 'bg-green-500' :
                            score >= 0.6 ? 'bg-blue-500' :
                            score >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${score * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-12">
                        {(score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
