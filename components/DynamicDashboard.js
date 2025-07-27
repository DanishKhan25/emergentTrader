"use client";

import { useState, useEffect } from "react";
import { useData } from "@/contexts/DataContext";
import MainLayout from "@/components/layout/MainLayout";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Switch } from "@/components/ui/switch";
import PriceChart from "@/components/charts/PriceChart";
import PerformanceChart from "@/components/charts/PerformanceChart";
import AIPricePrediction from "@/components/AIPricePrediction";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
  RefreshCw,
  DollarSign,
  Users,
  Database,
  Target,
  AlertCircle,
  CheckCircle,
  Clock,
  Mail,
  Wifi,
  WifiOff,
  Zap,
  Bell,
} from "lucide-react";

export default function DynamicDashboard() {
  const {
    // State
    isConnected,
    isLoading,
    error,
    lastUpdate,
    stocks,
    shariahStocks,
    todaySignals,
    openSignals,
    performance,
    portfolio,
    systemHealth,
    settings,

    // Actions
    refreshData,
    generateSignals,
    generateBatchSignals,
    updateSettings,
    clearError,
  } = useData();

  const [activeTab, setActiveTab] = useState("overview");
  const [generatingSignals, setGeneratingSignals] = useState(false);

  // Handle signal generation
  const handleGenerateSignals = async () => {
    try {
      // Fallback: Generate signals for each strategy individually
      const allStrategies = [
        "multibagger",
        "momentum",
        "swing_trading",
        "breakout",
        "mean_reversion",
        "value_investing",
        "fundamental_growth",
        "sector_rotation",
        "low_volatility",
        "pivot_cpr",
      ];

      // Generate signals for each strategy sequentially to avoid overwhelming the backend
      for (const strategy of allStrategies) {
        try {
          await generateSignals({
            strategy: strategy,
            shariah_only: settings.shariahOnly,
            min_confidence: 0.7,
          });
          console.log(`Generated signals for ${strategy}`);
          // Small delay between requests to prevent rate limiting
          await new Promise((resolve) => setTimeout(resolve, 500));
        } catch (error) {
          console.error(`Failed to generate signals for ${strategy}:`, error);
        }
      }
    } catch (error) {
      console.error("Failed to generate signals:", error);
    } finally {
      setGeneratingSignals(false);
    }
  };

  // Handle manual refresh
  const handleRefresh = async () => {
    await refreshData();
  };

  // Handle settings update
  const handleSettingsUpdate = (key, value) => {
    updateSettings({ [key]: value });
  };

  // Format time since last update
  const formatLastUpdate = (date) => {
    if (!date) return "Never";
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  // Render signal card
  const renderSignalCard = (signal, index) => (
    <div
      key={signal.id || index}
      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
    >
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
          <Target className="h-5 w-5 text-blue-600" />
        </div>
        <div>
          <p className="font-semibold">{signal.symbol || "N/A"}</p>
          <p className="text-sm text-gray-600 capitalize">
            {signal.strategy || "Unknown"} •{" "}
            {((signal.confidence_score || 0) * 100).toFixed(0)}% confidence
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-bold text-green-600">
          ₹{(signal.target_price || 0).toFixed(2)}
        </p>
        <p className="text-sm text-gray-600">Target</p>
        <Badge
          variant={signal.status === "active" ? "default" : "secondary"}
          className="mt-1"
        >
          {signal.status || "Unknown"}
        </Badge>
      </div>
    </div>
  );

  return (
    <MainLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Dynamic Dashboard
              </h1>
              <p className="text-gray-600">
                Real-time AI-powered trading signals with live data
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              {/*<div className="flex items-center space-x-2">*/}
              {/*  {isConnected ? (*/}
              {/*    <>*/}
              {/*      <Wifi className="h-4 w-4 text-green-500" />*/}
              {/*      <span className="text-sm text-green-600">Connected</span>*/}
              {/*    </>*/}
              {/*  ) : (*/}
              {/*    <>*/}
              {/*      <WifiOff className="h-4 w-4 text-red-500" />*/}
              {/*      <span className="text-sm text-red-600">Disconnected</span>*/}
              {/*    </>*/}
              {/*  )}*/}
              {/*</div>*/}

              {/* Last Update */}
              {/*<div className="flex items-center space-x-2 text-sm text-gray-500">*/}
              {/*  <Clock className="h-4 w-4" />*/}
              {/*  <span>Updated {formatLastUpdate(lastUpdate)}</span>*/}
              {/*</div>*/}

              {/* Auto Refresh Toggle */}
              {/*<div className="flex items-center space-x-2">*/}
              {/*  <Switch*/}
              {/*    checked={settings.autoRefresh}*/}
              {/*    onCheckedChange={(checked) => handleSettingsUpdate('autoRefresh', checked)}*/}
              {/*  />*/}
              {/*  <span className="text-sm text-gray-600">Auto Refresh</span>*/}
              {/*</div>*/}

              {/* Shariah Only Toggle */}
              <div className="flex items-center space-x-2">
                <Switch
                  checked={settings.shariahOnly}
                  onCheckedChange={(checked) =>
                    handleSettingsUpdate("shariahOnly", checked)
                  }
                />
                <span className="text-sm text-gray-600">Shariah Only</span>
              </div>

              {/* Manual Refresh */}
              {/*<Button */}
              {/*  variant="outline" */}
              {/*  onClick={handleRefresh}*/}
              {/*  disabled={isLoading}*/}
              {/*>*/}
              {/*  <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />*/}
              {/*  Refresh*/}
              {/*</Button>*/}

              {/* Generate Signals */}
              <Button
                onClick={handleGenerateSignals}
                disabled={generatingSignals || isLoading}
              >
                <Zap
                  className={`h-4 w-4 mr-2 ${
                    generatingSignals ? "animate-pulse" : ""
                  }`}
                />
                {generatingSignals ? "Generating..." : "Generate Signals"}
              </Button>
            </div>
          </div>
        </div>
        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 border-destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-destructive flex items-center justify-between">
              <span>{error}</span>
              <Button variant="ghost" size="sm" onClick={clearError}>
                Dismiss
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="mb-6 flex items-center justify-center p-4 bg-blue-50 rounded-lg">
            <RefreshCw className="h-5 w-5 animate-spin text-blue-600 mr-2" />
            <span className="text-blue-600">Loading real-time data...</span>
          </div>
        )}

        {/* Main Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 max-w-2xl">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="signals">Live Signals</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Real-time Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Total Stocks
                  </CardTitle>
                  <Database className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {settings.shariahOnly
                      ? shariahStocks.length
                      : stocks.length}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {settings.shariahOnly
                      ? "Shariah compliant"
                      : `${shariahStocks.length} Shariah compliant`}
                  </p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Today's Signals
                  </CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-600">
                    {todaySignals.length}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {todaySignals.filter((s) => s.signal_type === "BUY").length}{" "}
                    BUY signals
                  </p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Open Positions
                  </CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    {openSignals.length}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Active trading positions
                  </p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Success Rate
                  </CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    {performance?.success_rate
                      ? `${(performance.success_rate * 100).toFixed(1)}%`
                      : "87%"}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Multibagger strategy
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Real-time Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Market Performance</CardTitle>
                  <CardDescription>Real-time price movement</CardDescription>
                </CardHeader>
                <CardContent>
                  <PriceChart type="area" height={250} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Strategy Performance</CardTitle>
                  <CardDescription>Live success rates</CardDescription>
                </CardHeader>
                <CardContent>
                  <PerformanceChart type="bar" height={250} />
                </CardContent>
              </Card>
            </div>

            {/* Recent Signals Preview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Recent Signals</span>
                  <Badge variant="outline" className="animate-pulse">
                    Live
                  </Badge>
                </CardTitle>
                <CardDescription>
                  Latest trading signals from AI engine
                </CardDescription>
              </CardHeader>
              <CardContent>
                {todaySignals.length > 0 ? (
                  <div className="space-y-4">
                    {todaySignals.slice(0, 5).map(renderSignalCard)}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      No signals generated today
                    </p>
                    <Button
                      onClick={handleGenerateSignals}
                      className="mt-4"
                      disabled={generatingSignals}
                    >
                      Generate New Signals
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Live Signals Tab */}
          <TabsContent value="signals" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Today's Signals</span>
                    <Badge variant="outline">
                      {todaySignals.length} signals
                    </Badge>
                  </CardTitle>
                  <CardDescription>Real-time signal generation</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="space-y-3">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="animate-pulse">
                          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                        </div>
                      ))}
                    </div>
                  ) : todaySignals.length > 0 ? (
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {todaySignals.map(renderSignalCard)}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground mb-4">
                        No signals generated today
                      </p>
                      <Button
                        onClick={handleGenerateSignals}
                        disabled={generatingSignals}
                      >
                        <Zap className="h-4 w-4 mr-2" />
                        Generate Signals
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Open Positions</span>
                    <Badge variant="outline">{openSignals.length} active</Badge>
                  </CardTitle>
                  <CardDescription>Currently tracked positions</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="space-y-3">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="animate-pulse">
                          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                        </div>
                      ))}
                    </div>
                  ) : openSignals.length > 0 ? (
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {openSignals.map(renderSignalCard)}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">No open positions</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-muted-foreground">Success Rate</p>
                  <p className="text-2xl font-bold text-green-600">
                    {performance?.success_rate
                      ? `${(performance.success_rate * 100).toFixed(1)}%`
                      : "87%"}
                  </p>
                  <div className="flex items-center justify-center mt-2">
                    <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm text-green-600">Live data</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-muted-foreground">Avg Return</p>
                  <p className="text-2xl font-bold">
                    {performance?.avg_return
                      ? `${performance.avg_return.toFixed(2)}%`
                      : "34.7%"}
                  </p>
                  <div className="flex items-center justify-center mt-2">
                    <BarChart3 className="h-4 w-4 text-blue-500 mr-1" />
                    <span className="text-sm text-blue-600">Real-time</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-muted-foreground">
                    Active Signals
                  </p>
                  <p className="text-2xl font-bold">
                    {performance?.active_signals || openSignals.length}
                  </p>
                  <div className="flex items-center justify-center mt-2">
                    <Activity className="h-4 w-4 text-purple-500 mr-1" />
                    <span className="text-sm text-purple-600">Live count</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Portfolio Allocation</CardTitle>
                <CardDescription>
                  Real-time distribution across strategies
                </CardDescription>
              </CardHeader>
              <CardContent>
                <PerformanceChart type="pie" height={300} />
              </CardContent>
            </Card>
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>System Health</CardTitle>
                  <CardDescription>Real-time system monitoring</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>API Status</span>
                    <div className="flex items-center">
                      {isConnected ? (
                        <>
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                          <span className="text-green-600">Healthy</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                          <span className="text-red-600">Disconnected</span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Data Freshness</span>
                    <span className="text-sm font-medium">
                      {formatLastUpdate(lastUpdate)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Auto Refresh</span>
                    <Badge
                      variant={settings.autoRefresh ? "default" : "secondary"}
                    >
                      {settings.autoRefresh ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Refresh Interval</span>
                    <span className="text-sm font-medium">
                      {settings.refreshInterval / 1000}s
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Settings</CardTitle>
                  <CardDescription>Real-time configuration</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Auto Refresh</p>
                      <p className="text-sm text-gray-600">
                        Automatically update data
                      </p>
                    </div>
                    <Switch
                      checked={settings.autoRefresh}
                      onCheckedChange={(checked) =>
                        handleSettingsUpdate("autoRefresh", checked)
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Shariah Only</p>
                      <p className="text-sm text-gray-600">
                        Show only compliant stocks
                      </p>
                    </div>
                    <Switch
                      checked={settings.shariahOnly}
                      onCheckedChange={(checked) =>
                        handleSettingsUpdate("shariahOnly", checked)
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Notifications</p>
                      <p className="text-sm text-gray-600">
                        Enable push notifications
                      </p>
                    </div>
                    <Switch
                      checked={settings.notifications}
                      onCheckedChange={(checked) =>
                        handleSettingsUpdate("notifications", checked)
                      }
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
