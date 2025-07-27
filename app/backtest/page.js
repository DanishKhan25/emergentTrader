'use client'

import {useState, useEffect} from 'react'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {Input} from '@/components/ui/input'
import {Label} from '@/components/ui/label'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'
import {Badge} from '@/components/ui/badge'
import {Tabs, TabsContent, TabsList, TabsTrigger} from '@/components/ui/tabs'
import {Progress} from '@/components/ui/progress'
import {Alert, AlertDescription} from '@/components/ui/alert'
import {
    Play,
    Pause,
    RotateCcw,
    TrendingUp,
    TrendingDown,
    Target,
    Shield,
    Calendar,
    DollarSign,
    BarChart3,
    PieChart,
    Activity,
    Clock,
    CheckCircle,
    XCircle,
    AlertTriangle
} from 'lucide-react'
import MainLayout from "@/components/layout/MainLayout";

export default function BacktestPage() {
    const [strategies, setStrategies] = useState([])
    const [selectedStrategy, setSelectedStrategy] = useState('')
    const [backtestConfig, setBacktestConfig] = useState({
        startDate: '2023-01-01',
        endDate: '2024-12-31',
        initialCapital: 1000000,
        maxPositions: 10,
        positionSize: 100000,
        stopLoss: 5,
        takeProfit: 15,
        commission: 0.1
    })
    const [backtestResults, setBacktestResults] = useState(null)
    const [isRunning, setIsRunning] = useState(false)
    const [progress, setProgress] = useState(0)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Fetch available strategies
    useEffect(() => {
        fetchStrategies()
    }, [])

    const fetchStrategies = async () => {
        try {
            const response = await fetch('http://localhost:8000/strategies')
            const data = await response.json()

            if (data.success) {
                setStrategies(data.data || [])
            } else {
                setError('Failed to load strategies')
            }
        } catch (err) {
            setError('Error connecting to backend')
        } finally {
            setLoading(false)
        }
    }

    const runBacktest = async () => {
        if (!selectedStrategy) {
            setError('Please select a strategy')
            return
        }

        setIsRunning(true)
        setProgress(0)
        setError(null)

        try {
            // Simulate progress
            const progressInterval = setInterval(() => {
                setProgress(prev => {
                    if (prev >= 90) {
                        clearInterval(progressInterval)
                        return 90
                    }
                    return prev + 10
                })
            }, 500)

            const response = await fetch('http://localhost:8000/backtest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    strategy: selectedStrategy,
                    ...backtestConfig
                })
            })

            const data = await response.json()
            clearInterval(progressInterval)
            setProgress(100)

            if (data.success) {
                setBacktestResults(data.data)
            } else {
                setError(data.error || 'Backtest failed')
            }
        } catch (err) {
            setError('Error running backtest: ' + err.message)
        } finally {
            setIsRunning(false)
            setTimeout(() => setProgress(0), 2000)
        }
    }

    const resetBacktest = () => {
        setBacktestResults(null)
        setProgress(0)
        setError(null)
    }

    if (loading) {
        return (
            <div className="container mx-auto p-6">
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-2">Loading strategies...</span>
                </div>
            </div>
        )
    }

    return (
        <MainLayout>
            <div className="container mx-auto p-6 space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">Strategy Backtesting</h1>
                        <p className="text-gray-600 mt-1">Test your trading strategies against historical data</p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            onClick={runBacktest}
                            disabled={isRunning || !selectedStrategy}
                            className="bg-blue-600 hover:bg-blue-700"
                        >
                            {isRunning ? (
                                <>
                                    <Pause className="h-4 w-4 mr-2"/>
                                    Running...
                                </>
                            ) : (
                                <>
                                    <Play className="h-4 w-4 mr-2"/>
                                    Run Backtest
                                </>
                            )}
                        </Button>
                        <Button variant="outline" onClick={resetBacktest}>
                            <RotateCcw className="h-4 w-4 mr-2"/>
                            Reset
                        </Button>
                    </div>
                </div>

                {/* Error Alert */}
                {error && (
                    <Alert variant="destructive">
                        <AlertTriangle className="h-4 w-4"/>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {/* Progress Bar */}
                {isRunning && (
                    <Card>
                        <CardContent className="pt-6">
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span>Running backtest...</span>
                                    <span>{progress}%</span>
                                </div>
                                <Progress value={progress} className="w-full"/>
                            </div>
                        </CardContent>
                    </Card>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Configuration Panel */}
                    <div className="lg:col-span-1">
                        <Card>
                            <CardHeader>
                                <CardTitle>Backtest Configuration</CardTitle>
                                <CardDescription>Configure your backtest parameters</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {/* Strategy Selection */}
                                <div className="space-y-2">
                                    <Label htmlFor="strategy">Strategy</Label>
                                    <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select a strategy"/>
                                        </SelectTrigger>
                                        <SelectContent>
                                            {strategies.map((strategy) => (
                                                <SelectItem key={strategy.name} value={strategy.name}>
                                                    <div className="flex items-center gap-2">
                                                        <span>{strategy.name}</span>
                                                        <Badge variant="secondary" className="text-xs">
                                                            {strategy.success_rate}%
                                                        </Badge>
                                                    </div>
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                {/* Date Range */}
                                <div className="grid grid-cols-2 gap-2">
                                    <div className="space-y-2">
                                        <Label htmlFor="startDate">Start Date</Label>
                                        <Input
                                            id="startDate"
                                            type="date"
                                            value={backtestConfig.startDate}
                                            onChange={(e) => setBacktestConfig(prev => ({
                                                ...prev,
                                                startDate: e.target.value
                                            }))}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="endDate">End Date</Label>
                                        <Input
                                            id="endDate"
                                            type="date"
                                            value={backtestConfig.endDate}
                                            onChange={(e) => setBacktestConfig(prev => ({
                                                ...prev,
                                                endDate: e.target.value
                                            }))}
                                        />
                                    </div>
                                </div>

                                {/* Capital Settings */}
                                <div className="space-y-2">
                                    <Label htmlFor="initialCapital">Initial Capital (₹)</Label>
                                    <Input
                                        id="initialCapital"
                                        type="number"
                                        value={backtestConfig.initialCapital}
                                        onChange={(e) => setBacktestConfig(prev => ({
                                            ...prev,
                                            initialCapital: parseInt(e.target.value)
                                        }))}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="positionSize">Position Size (₹)</Label>
                                    <Input
                                        id="positionSize"
                                        type="number"
                                        value={backtestConfig.positionSize}
                                        onChange={(e) => setBacktestConfig(prev => ({
                                            ...prev,
                                            positionSize: parseInt(e.target.value)
                                        }))}
                                    />
                                </div>

                                {/* Risk Management */}
                                <div className="grid grid-cols-2 gap-2">
                                    <div className="space-y-2">
                                        <Label htmlFor="stopLoss">Stop Loss (%)</Label>
                                        <Input
                                            id="stopLoss"
                                            type="number"
                                            step="0.1"
                                            value={backtestConfig.stopLoss}
                                            onChange={(e) => setBacktestConfig(prev => ({
                                                ...prev,
                                                stopLoss: parseFloat(e.target.value)
                                            }))}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="takeProfit">Take Profit (%)</Label>
                                        <Input
                                            id="takeProfit"
                                            type="number"
                                            step="0.1"
                                            value={backtestConfig.takeProfit}
                                            onChange={(e) => setBacktestConfig(prev => ({
                                                ...prev,
                                                takeProfit: parseFloat(e.target.value)
                                            }))}
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="commission">Commission (%)</Label>
                                    <Input
                                        id="commission"
                                        type="number"
                                        step="0.01"
                                        value={backtestConfig.commission}
                                        onChange={(e) => setBacktestConfig(prev => ({
                                            ...prev,
                                            commission: parseFloat(e.target.value)
                                        }))}
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Results Panel */}
                    <div className="lg:col-span-2">
                        {backtestResults ? (
                            <Tabs defaultValue="overview" className="space-y-4">
                                <TabsList className="grid w-full grid-cols-4">
                                    <TabsTrigger value="overview">Overview</TabsTrigger>
                                    <TabsTrigger value="performance">Performance</TabsTrigger>
                                    <TabsTrigger value="trades">Trades</TabsTrigger>
                                    <TabsTrigger value="analysis">Analysis</TabsTrigger>
                                </TabsList>

                                {/* Overview Tab */}
                                <TabsContent value="overview" className="space-y-4">
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <Card>
                                            <CardContent className="pt-6">
                                                <div className="flex items-center gap-2">
                                                    <DollarSign className="h-4 w-4 text-green-600"/>
                                                    <div>
                                                        <p className="text-sm text-gray-600">Total Return</p>
                                                        <p className="text-2xl font-bold text-green-600">
                                                            {backtestResults.totalReturn > 0 ? '+' : ''}
                                                            {backtestResults.totalReturn?.toFixed(2)}%
                                                        </p>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>

                                        <Card>
                                            <CardContent className="pt-6">
                                                <div className="flex items-center gap-2">
                                                    <Target className="h-4 w-4 text-blue-600"/>
                                                    <div>
                                                        <p className="text-sm text-gray-600">Win Rate</p>
                                                        <p className="text-2xl font-bold text-blue-600">
                                                            {backtestResults.winRate?.toFixed(1)}%
                                                        </p>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>

                                        <Card>
                                            <CardContent className="pt-6">
                                                <div className="flex items-center gap-2">
                                                    <BarChart3 className="h-4 w-4 text-purple-600"/>
                                                    <div>
                                                        <p className="text-sm text-gray-600">Total Trades</p>
                                                        <p className="text-2xl font-bold text-purple-600">
                                                            {backtestResults.totalTrades || 0}
                                                        </p>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>

                                        <Card>
                                            <CardContent className="pt-6">
                                                <div className="flex items-center gap-2">
                                                    <Shield className="h-4 w-4 text-orange-600"/>
                                                    <div>
                                                        <p className="text-sm text-gray-600">Max Drawdown</p>
                                                        <p className="text-2xl font-bold text-orange-600">
                                                            -{backtestResults.maxDrawdown?.toFixed(2)}%
                                                        </p>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    </div>

                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Performance Summary</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="grid grid-cols-2 gap-6">
                                                <div className="space-y-3">
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-600">Initial Capital:</span>
                                                        <span
                                                            className="font-medium">₹{backtestConfig.initialCapital.toLocaleString()}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-600">Final Capital:</span>
                                                        <span
                                                            className="font-medium">₹{backtestResults.finalCapital?.toLocaleString()}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-600">Profit/Loss:</span>
                                                        <span
                                                            className={`font-medium ${backtestResults.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ₹{backtestResults.totalPnL?.toLocaleString()}
                          </span>
                                                    </div>
                                                </div>
                                                <div className="space-y-3">
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-600">Winning Trades:</span>
                                                        <span
                                                            className="font-medium text-green-600">{backtestResults.winningTrades || 0}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-600">Losing Trades:</span>
                                                        <span
                                                            className="font-medium text-red-600">{backtestResults.losingTrades || 0}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-600">Avg Trade Duration:</span>
                                                        <span
                                                            className="font-medium">{backtestResults.avgTradeDuration || 0} days</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </TabsContent>

                                {/* Performance Tab */}
                                <TabsContent value="performance" className="space-y-4">
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Performance Metrics</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="grid grid-cols-2 gap-6">
                                                <div className="space-y-4">
                                                    <h4 className="font-semibold">Risk Metrics</h4>
                                                    <div className="space-y-2">
                                                        <div className="flex justify-between">
                                                            <span>Sharpe Ratio:</span>
                                                            <span
                                                                className="font-medium">{backtestResults.sharpeRatio?.toFixed(2) || 'N/A'}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span>Volatility:</span>
                                                            <span
                                                                className="font-medium">{backtestResults.volatility?.toFixed(2)}%</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span>Beta:</span>
                                                            <span
                                                                className="font-medium">{backtestResults.beta?.toFixed(2) || 'N/A'}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="space-y-4">
                                                    <h4 className="font-semibold">Trade Metrics</h4>
                                                    <div className="space-y-2">
                                                        <div className="flex justify-between">
                                                            <span>Avg Win:</span>
                                                            <span
                                                                className="font-medium text-green-600">₹{backtestResults.avgWin?.toLocaleString() || 0}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span>Avg Loss:</span>
                                                            <span
                                                                className="font-medium text-red-600">₹{backtestResults.avgLoss?.toLocaleString() || 0}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span>Profit Factor:</span>
                                                            <span
                                                                className="font-medium">{backtestResults.profitFactor?.toFixed(2) || 'N/A'}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </TabsContent>

                                {/* Trades Tab */}
                                <TabsContent value="trades" className="space-y-4">
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Trade History</CardTitle>
                                            <CardDescription>Detailed list of all trades executed during
                                                backtest</CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="space-y-2 max-h-96 overflow-y-auto">
                                                {backtestResults.trades?.map((trade, index) => (
                                                    <div key={index}
                                                         className="flex items-center justify-between p-3 border rounded-lg">
                                                        <div className="flex items-center gap-3">
                                                            {trade.pnl >= 0 ? (
                                                                <CheckCircle className="h-4 w-4 text-green-600"/>
                                                            ) : (
                                                                <XCircle className="h-4 w-4 text-red-600"/>
                                                            )}
                                                            <div>
                                                                <p className="font-medium">{trade.symbol}</p>
                                                                <p className="text-sm text-gray-600">
                                                                    {trade.entryDate} → {trade.exitDate}
                                                                </p>
                                                            </div>
                                                        </div>
                                                        <div className="text-right">
                                                            <p className={`font-medium ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                                {trade.pnl >= 0 ? '+' : ''}₹{trade.pnl?.toLocaleString()}
                                                            </p>
                                                            <p className="text-sm text-gray-600">
                                                                {trade.pnlPercent >= 0 ? '+' : ''}{trade.pnlPercent?.toFixed(2)}%
                                                            </p>
                                                        </div>
                                                    </div>
                                                )) || (
                                                    <p className="text-center text-gray-500 py-8">No trades
                                                        available</p>
                                                )}
                                            </div>
                                        </CardContent>
                                    </Card>
                                </TabsContent>

                                {/* Analysis Tab */}
                                <TabsContent value="analysis" className="space-y-4">
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Strategy Analysis</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="space-y-4">
                                                <div>
                                                    <h4 className="font-semibold mb-2">Strengths</h4>
                                                    <ul className="space-y-1 text-sm text-gray-600">
                                                        {backtestResults.analysis?.strengths?.map((strength, index) => (
                                                            <li key={index} className="flex items-center gap-2">
                                                                <CheckCircle className="h-3 w-3 text-green-600"/>
                                                                {strength}
                                                            </li>
                                                        )) || (
                                                            <li>Analysis not available</li>
                                                        )}
                                                    </ul>
                                                </div>
                                                <div>
                                                    <h4 className="font-semibold mb-2">Areas for Improvement</h4>
                                                    <ul className="space-y-1 text-sm text-gray-600">
                                                        {backtestResults.analysis?.improvements?.map((improvement, index) => (
                                                            <li key={index} className="flex items-center gap-2">
                                                                <AlertTriangle className="h-3 w-3 text-orange-600"/>
                                                                {improvement}
                                                            </li>
                                                        )) || (
                                                            <li>Analysis not available</li>
                                                        )}
                                                    </ul>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </TabsContent>
                            </Tabs>
                        ) : (
                            <Card className="h-96 flex items-center justify-center">
                                <div className="text-center space-y-4">
                                    <Activity className="h-12 w-12 text-gray-400 mx-auto"/>
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-600">No Backtest Results</h3>
                                        <p className="text-gray-500">Configure your parameters and run a backtest to see
                                            results</p>
                                    </div>
                                </div>
                            </Card>
                        )}
                    </div>
                </div>
            </div>

        </MainLayout>
    )
}
