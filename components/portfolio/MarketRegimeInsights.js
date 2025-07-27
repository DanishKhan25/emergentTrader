'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Zap,
  Target,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw,
  Lightbulb
} from 'lucide-react'

export default function MarketRegimeInsights({ portfolioData, onRecommendation }) {
  const [marketRegime, setMarketRegime] = useState(null)
  const [positionAnalysis, setPositionAnalysis] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadMarketRegimeInsights()
  }, [portfolioData])

  const loadMarketRegimeInsights = async () => {
    setLoading(true)
    try {
      // Get market regime
      const regimeResponse = await fetch('http://localhost:8000/market-regime/summary')
      const regimeData = await regimeResponse.json()
      
      if (regimeData.success) {
        setMarketRegime(regimeData.data)
        
        // Analyze each position against current regime
        if (portfolioData?.positions) {
          await analyzePositions(regimeData.data, portfolioData.positions)
        }
      }
    } catch (error) {
      console.error('Error loading market regime insights:', error)
    } finally {
      setLoading(false)
    }
  }

  const analyzePositions = async (regime, positions) => {
    const analysis = []
    
    for (const [positionId, position] of Object.entries(positions)) {
      if (position.status !== 'active') continue
      
      try {
        // Get timing score for this position's strategy
        const timingResponse = await fetch('http://localhost:8000/market-regime/timing-score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            signal_data: {
              symbol: position.symbol,
              strategy: position.strategy,
              confidence: position.confidence || 0.8
            }
          })
        })
        
        const timingData = await timingResponse.json()
        
        if (timingData.success) {
          analysis.push({
            positionId,
            ...position,
            timing: timingData.data,
            regimeCompatibility: timingData.data.regime_compatibility
          })
        }
      } catch (error) {
        console.error(`Error analyzing position ${position.symbol}:`, error)
      }
    }
    
    setPositionAnalysis(analysis)
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

  const getTimingCategoryColor = (category) => {
    switch (category) {
      case 'excellent': return 'text-green-600 bg-green-50 border-green-200'
      case 'good': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'poor': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getTimingIcon = (category) => {
    switch (category) {
      case 'excellent': return <CheckCircle className="h-4 w-4" />
      case 'good': return <Target className="h-4 w-4" />
      case 'moderate': return <Clock className="h-4 w-4" />
      case 'poor': return <AlertTriangle className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  const generateRecommendations = () => {
    if (!positionAnalysis.length) return []

    const recommendations = []

    // Analyze positions by timing category
    const excellentPositions = positionAnalysis.filter(p => p.timing?.timing_category === 'excellent')
    const poorPositions = positionAnalysis.filter(p => p.timing?.timing_category === 'poor')
    const moderatePositions = positionAnalysis.filter(p => p.timing?.timing_category === 'moderate')

    if (excellentPositions.length > 0) {
      recommendations.push({
        type: 'opportunity',
        title: 'Consider Increasing Positions',
        message: `${excellentPositions.length} positions have excellent timing in current market regime`,
        positions: excellentPositions.map(p => p.symbol),
        action: 'Consider adding to these positions'
      })
    }

    if (poorPositions.length > 0) {
      recommendations.push({
        type: 'warning',
        title: 'Review These Positions',
        message: `${poorPositions.length} positions have poor timing in current market regime`,
        positions: poorPositions.map(p => p.symbol),
        action: 'Consider reducing exposure or setting tighter stop losses'
      })
    }

    if (moderatePositions.length > 0) {
      recommendations.push({
        type: 'info',
        title: 'Monitor Closely',
        message: `${moderatePositions.length} positions have moderate timing - watch for regime changes`,
        positions: moderatePositions.map(p => p.symbol),
        action: 'Monitor for regime changes that could improve timing'
      })
    }

    return recommendations
  }

  const recommendations = generateRecommendations()

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin mr-2" />
            <span>Analyzing market regime insights...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!marketRegime) {
    return (
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Market regime data unavailable. Portfolio analysis may be limited.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Market Regime Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getRegimeIcon(marketRegime.current_regime)}
            Market Regime Impact
          </CardTitle>
          <CardDescription>
            How current market conditions affect your portfolio
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
            <Button onClick={loadMarketRegimeInsights} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
          
          <p className="text-sm text-gray-600">
            {marketRegime.description}
          </p>
        </CardContent>
      </Card>

      {/* Position Analysis */}
      {positionAnalysis.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Position Timing Analysis</CardTitle>
            <CardDescription>
              How well your positions align with current market regime
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {positionAnalysis.map((position) => (
                <div key={position.positionId} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="font-medium">{position.symbol}</div>
                      <Badge variant="outline" className="text-xs">
                        {position.strategy}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      {getTimingIcon(position.timing?.timing_category)}
                      <Badge className={getTimingCategoryColor(position.timing?.timing_category)}>
                        {position.timing?.timing_category?.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500">Timing Score</div>
                      <div className="font-medium">
                        {position.timing?.timing_score ? 
                          (position.timing.timing_score * 100).toFixed(0) + '%' : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500">Regime Fit</div>
                      <div className="font-medium">
                        {position.regimeCompatibility ? 
                          (position.regimeCompatibility * 100).toFixed(0) + '%' : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500">Quantity</div>
                      <div className="font-medium">{position.quantity} shares</div>
                    </div>
                    <div>
                      <div className="text-gray-500">Current Value</div>
                      <div className="font-medium">₹{(position.current_value || 0).toLocaleString()}</div>
                    </div>
                  </div>
                  
                  {position.timing?.recommendation && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-md">
                      <div className="text-sm text-gray-700">
                        <strong>Recommendation:</strong> {position.timing.recommendation}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              Market Regime Recommendations
            </CardTitle>
            <CardDescription>
              Actionable insights based on current market conditions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recommendations.map((rec, index) => (
                <Alert key={index} className={
                  rec.type === 'opportunity' ? 'border-green-200 bg-green-50' :
                  rec.type === 'warning' ? 'border-red-200 bg-red-50' :
                  'border-blue-200 bg-blue-50'
                }>
                  <div className="flex items-start gap-3">
                    {rec.type === 'opportunity' ? (
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    ) : rec.type === 'warning' ? (
                      <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                    ) : (
                      <Lightbulb className="h-5 w-5 text-blue-600 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <AlertDescription>
                        <div className="font-medium mb-1">{rec.title}</div>
                        <div className="text-sm mb-2">{rec.message}</div>
                        <div className="text-sm">
                          <strong>Positions:</strong> {rec.positions.join(', ')}
                        </div>
                        <div className="text-sm mt-1">
                          <strong>Action:</strong> {rec.action}
                        </div>
                      </AlertDescription>
                    </div>
                  </div>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Portfolio Regime Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Regime Alignment</CardTitle>
          <CardDescription>
            Overall portfolio performance in current market regime
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {positionAnalysis.filter(p => p.timing?.timing_category === 'excellent').length}
              </div>
              <div className="text-sm text-gray-600">Excellent Timing</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {positionAnalysis.filter(p => p.timing?.timing_category === 'good').length}
              </div>
              <div className="text-sm text-gray-600">Good Timing</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {positionAnalysis.filter(p => p.timing?.timing_category === 'moderate').length}
              </div>
              <div className="text-sm text-gray-600">Moderate Timing</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {positionAnalysis.filter(p => p.timing?.timing_category === 'poor').length}
              </div>
              <div className="text-sm text-gray-600">Poor Timing</div>
            </div>
          </div>
          
          {positionAnalysis.length > 0 && (
            <div className="mt-4">
              <div className="text-sm text-gray-600 mb-2">Portfolio Regime Alignment</div>
              <Progress 
                value={
                  (positionAnalysis.filter(p => 
                    ['excellent', 'good'].includes(p.timing?.timing_category)
                  ).length / positionAnalysis.length) * 100
                } 
                className="h-2"
              />
              <div className="text-xs text-gray-500 mt-1">
                {((positionAnalysis.filter(p => 
                  ['excellent', 'good'].includes(p.timing?.timing_category)
                ).length / positionAnalysis.length) * 100).toFixed(0)}% of positions well-aligned with current regime
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
