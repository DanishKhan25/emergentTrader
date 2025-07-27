import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Brain, 
  Target, 
  Shield, 
  AlertTriangle,
  BarChart3,
  Clock,
  Zap
} from 'lucide-react';

const AIPricePrediction = () => {
  const [symbol, setSymbol] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelPerformance, setModelPerformance] = useState(null);
  const [trainedModels, setTrainedModels] = useState([]);

  // Fetch trained models on component mount
  useEffect(() => {
    fetchTrainedModels();
  }, []);

  const fetchTrainedModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/ai/models/list');
      const data = await response.json();
      if (data.success) {
        setTrainedModels(data.data.models || []);
      }
    } catch (error) {
      console.error('Error fetching trained models:', error);
    }
  };

  const generatePrediction = async (daysAhead = 1) => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/ai/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol.toUpperCase(),
          days_ahead: daysAhead,
          retrain: false
        }),
      });

      const data = await response.json();

      if (data.success) {
        setPrediction(data.data);
      } else {
        setError(data.error || 'Failed to generate prediction');
      }
    } catch (error) {
      setError('Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const trainModel = async () => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/ai/train', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol.toUpperCase(),
          retrain: true
        }),
      });

      const data = await response.json();

      if (data.success) {
        setError(null);
        // Show success message
        setTimeout(() => {
          fetchTrainedModels();
        }, 2000);
      } else {
        setError(data.error || 'Failed to start training');
      }
    } catch (error) {
      setError('Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const getModelPerformance = async () => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/ai/model/performance/${symbol.toUpperCase()}`);
      const data = await response.json();

      if (data.success) {
        setModelPerformance(data.data);
      } else {
        setError(data.error || 'Failed to get model performance');
      }
    } catch (error) {
      setError('Network error: ' + error.message);
    }
  };

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'BULLISH':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'BEARISH':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getTrendColor = (direction) => {
    switch (direction) {
      case 'BULLISH':
        return 'text-green-600 bg-green-50';
      case 'BEARISH':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-yellow-600 bg-yellow-50';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskColor = (risk) => {
    if (risk <= 30) return 'text-green-600';
    if (risk <= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-500" />
            AI Price Predictions
            <Badge variant="secondary" className="ml-2">
              <Zap className="h-3 w-3 mr-1" />
              ML Powered
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">Stock Symbol</label>
              <Input
                type="text"
                placeholder="Enter symbol (e.g., RELIANCE, TCS)"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="uppercase"
              />
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => generatePrediction(1)} 
                disabled={loading}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {loading ? 'Predicting...' : 'Predict 1D'}
              </Button>
              <Button 
                onClick={() => generatePrediction(7)} 
                disabled={loading}
                variant="outline"
              >
                Predict 7D
              </Button>
              <Button 
                onClick={() => generatePrediction(30)} 
                disabled={loading}
                variant="outline"
              >
                Predict 30D
              </Button>
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button 
              onClick={trainModel} 
              disabled={loading}
              variant="secondary"
              size="sm"
            >
              <Brain className="h-4 w-4 mr-2" />
              Train Model
            </Button>
            <Button 
              onClick={getModelPerformance} 
              disabled={loading}
              variant="outline"
              size="sm"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Performance
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Prediction Results */}
      {prediction && (
        <Tabs defaultValue="prediction" className="space-y-4">
          <TabsList>
            <TabsTrigger value="prediction">Prediction</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="levels">Support/Resistance</TabsTrigger>
          </TabsList>

          <TabsContent value="prediction">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Current Price */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Current Price</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">₹{prediction.current_price}</div>
                  <div className="text-sm text-gray-500">{prediction.symbol}</div>
                </CardContent>
              </Card>

              {/* 1 Day Prediction */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    1 Day Prediction
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">₹{prediction.predictions['1_day'].price}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge className={`${prediction.predictions['1_day'].change_percent >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {prediction.predictions['1_day'].change_percent >= 0 ? '+' : ''}{prediction.predictions['1_day'].change_percent}%
                    </Badge>
                    <span className={`text-sm ${getConfidenceColor(prediction.predictions['1_day'].confidence)}`}>
                      {prediction.predictions['1_day'].confidence}% confidence
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* 7 Day Prediction */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    7 Day Prediction
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">₹{prediction.predictions['7_day'].price}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge className={`${prediction.predictions['7_day'].change_percent >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {prediction.predictions['7_day'].change_percent >= 0 ? '+' : ''}{prediction.predictions['7_day'].change_percent}%
                    </Badge>
                    <span className={`text-sm ${getConfidenceColor(prediction.predictions['7_day'].confidence)}`}>
                      {prediction.predictions['7_day'].confidence}% confidence
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* 30 Day Prediction */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    30 Day Prediction
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">₹{prediction.predictions['30_day'].price}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge className={`${prediction.predictions['30_day'].change_percent >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {prediction.predictions['30_day'].change_percent >= 0 ? '+' : ''}{prediction.predictions['30_day'].change_percent}%
                    </Badge>
                    <span className={`text-sm ${getConfidenceColor(prediction.predictions['30_day'].confidence)}`}>
                      {prediction.predictions['30_day'].confidence}% confidence
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="analysis">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Trend Direction */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Trend Direction</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    {getTrendIcon(prediction.analysis.trend_direction)}
                    <Badge className={getTrendColor(prediction.analysis.trend_direction)}>
                      {prediction.analysis.trend_direction}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Model Accuracy */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Model Accuracy</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{prediction.analysis.model_accuracy}%</div>
                  <div className="text-sm text-gray-500">Historical performance</div>
                </CardContent>
              </Card>

              {/* Volatility Forecast */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Volatility</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{prediction.analysis.volatility_forecast}%</div>
                  <div className="text-sm text-gray-500">Expected volatility</div>
                </CardContent>
              </Card>

              {/* Risk Score */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Risk Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getRiskColor(prediction.analysis.risk_score)}`}>
                    {prediction.analysis.risk_score}%
                  </div>
                  <div className="text-sm text-gray-500">
                    {prediction.analysis.risk_score <= 30 ? 'Low Risk' : 
                     prediction.analysis.risk_score <= 60 ? 'Medium Risk' : 'High Risk'}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="levels">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Support Levels */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Target className="h-4 w-4 text-green-500" />
                    Support Levels
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {prediction.levels.support.map((level, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
                        <span className="text-sm font-medium">Support {index + 1}</span>
                        <span className="font-bold text-green-600">₹{level}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Resistance Levels */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Target className="h-4 w-4 text-red-500" />
                    Resistance Levels
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {prediction.levels.resistance.map((level, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-red-50 rounded">
                        <span className="text-sm font-medium">Resistance {index + 1}</span>
                        <span className="font-bold text-red-600">₹{level}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Metadata */}
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="text-sm font-medium">Prediction Metadata</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Features Used:</span>
                    <span className="ml-2">{prediction.metadata.features_count}</span>
                  </div>
                  <div>
                    <span className="font-medium">Generated:</span>
                    <span className="ml-2">{new Date(prediction.metadata.prediction_timestamp).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="font-medium">Horizon:</span>
                    <span className="ml-2">{prediction.metadata.days_ahead} day(s)</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Model Performance */}
      {modelPerformance && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Model Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(modelPerformance.horizons).map(([horizon, models]) => (
                <div key={horizon}>
                  <h4 className="font-medium mb-2 capitalize">{horizon} Predictions</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(models).map(([modelName, metrics]) => (
                      <div key={modelName} className="p-3 border rounded">
                        <div className="font-medium capitalize mb-2">{modelName.replace('_', ' ')}</div>
                        <div className="text-sm space-y-1">
                          <div>Accuracy: <span className="font-medium">{metrics.accuracy_percentage}%</span></div>
                          <div>R² Score: <span className="font-medium">{metrics.r2_score}</span></div>
                          <div>MAE: <span className="font-medium">{metrics.mae}</span></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trained Models List */}
      {trainedModels.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Available Trained Models</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trainedModels.map((model, index) => (
                <div key={index} className="p-3 border rounded">
                  <div className="font-medium">{model.symbol}</div>
                  <div className="text-sm text-gray-500 mt-1">
                    <div>Trained: {new Date(model.trained_at).toLocaleDateString()}</div>
                    <div>Features: {model.features_count}</div>
                    <div>Models: {model.model_types.join(', ')}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AIPricePrediction;
