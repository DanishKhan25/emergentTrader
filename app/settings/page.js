'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { 
  Settings, 
  Bell, 
  Shield, 
  Database,
  Mail,
  MessageSquare,
  DollarSign,
  Clock,
  Target,
  AlertTriangle,
  CheckCircle,
  Save,
  RefreshCw,
  Eye,
  EyeOff
} from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({})
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)
  const [activeTab, setActiveTab] = useState('general')

  // Mock settings data
  const mockSettings = {
    general: {
      systemName: 'EmergentTrader',
      timezone: 'Asia/Kolkata',
      currency: 'INR',
      language: 'en',
      theme: 'light',
      autoRefresh: true,
      refreshInterval: 30,
      shariahOnly: false
    },
    notifications: {
      emailNotifications: true,
      telegramNotifications: true,
      signalAlerts: true,
      targetHitAlerts: true,
      stopLossAlerts: true,
      dailyReports: true,
      weeklyReports: true,
      systemAlerts: true,
      emailAddress: 'trader@example.com',
      telegramChatId: '123456789'
    },
    trading: {
      defaultStrategy: 'multibagger',
      minConfidence: 0.7,
      maxPositions: 20,
      positionSizing: 'fixed',
      riskPerTrade: 2.0,
      stopLossPercent: 20.0,
      targetMultiplier: 2.0,
      autoExecution: false,
      paperTrading: true
    },
    api: {
      apiKey: 'sk-1234567890abcdef',
      apiUrl: 'http://localhost:8000',
      timeout: 30,
      retryAttempts: 3,
      rateLimitPerMinute: 60
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 60,
      ipWhitelist: '',
      apiKeyRotation: 30,
      auditLogging: true
    }
  }

  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setSettings(mockSettings)
      setLoading(false)
    }, 1000)
  }, [])

  const handleSave = async () => {
    setSaving(true)
    // Simulate API call
    setTimeout(() => {
      setSaving(false)
      // Show success message
    }, 2000)
  }

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }))
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="p-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 gap-6">
              {[...Array(3)].map((_, i) => (
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
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600 mt-2">
              Configure your trading system preferences and security settings.
            </p>
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </>
            )}
          </Button>
        </div>

        {/* Settings Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5 max-w-3xl">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="trading">Trading</TabsTrigger>
            <TabsTrigger value="api">API</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
          </TabsList>

          {/* General Settings */}
          <TabsContent value="general" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Settings className="h-5 w-5 mr-2" />
                  General Settings
                </CardTitle>
                <CardDescription>
                  Basic system configuration and preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="systemName">System Name</Label>
                    <Input
                      id="systemName"
                      value={settings.general?.systemName || ''}
                      onChange={(e) => updateSetting('general', 'systemName', e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="timezone">Timezone</Label>
                    <Select 
                      value={settings.general?.timezone || ''} 
                      onValueChange={(value) => updateSetting('general', 'timezone', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Asia/Kolkata">Asia/Kolkata (IST)</SelectItem>
                        <SelectItem value="America/New_York">America/New_York (EST)</SelectItem>
                        <SelectItem value="Europe/London">Europe/London (GMT)</SelectItem>
                        <SelectItem value="Asia/Tokyo">Asia/Tokyo (JST)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="currency">Currency</Label>
                    <Select 
                      value={settings.general?.currency || ''} 
                      onValueChange={(value) => updateSetting('general', 'currency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="INR">INR (₹)</SelectItem>
                        <SelectItem value="USD">USD ($)</SelectItem>
                        <SelectItem value="EUR">EUR (€)</SelectItem>
                        <SelectItem value="GBP">GBP (£)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="refreshInterval">Auto Refresh (seconds)</Label>
                    <Input
                      id="refreshInterval"
                      type="number"
                      value={settings.general?.refreshInterval || ''}
                      onChange={(e) => updateSetting('general', 'refreshInterval', parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="autoRefresh">Auto Refresh Data</Label>
                      <p className="text-sm text-gray-600">Automatically refresh market data</p>
                    </div>
                    <Switch
                      id="autoRefresh"
                      checked={settings.general?.autoRefresh || false}
                      onCheckedChange={(checked) => updateSetting('general', 'autoRefresh', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="shariahOnly">Shariah Compliant Only</Label>
                      <p className="text-sm text-gray-600">Show only Shariah-compliant stocks</p>
                    </div>
                    <Switch
                      id="shariahOnly"
                      checked={settings.general?.shariahOnly || false}
                      onCheckedChange={(checked) => updateSetting('general', 'shariahOnly', checked)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notification Settings */}
          <TabsContent value="notifications" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Bell className="h-5 w-5 mr-2" />
                  Notification Settings
                </CardTitle>
                <CardDescription>
                  Configure alerts and notification preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="emailAddress">Email Address</Label>
                    <Input
                      id="emailAddress"
                      type="email"
                      value={settings.notifications?.emailAddress || ''}
                      onChange={(e) => updateSetting('notifications', 'emailAddress', e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="telegramChatId">Telegram Chat ID</Label>
                    <Input
                      id="telegramChatId"
                      value={settings.notifications?.telegramChatId || ''}
                      onChange={(e) => updateSetting('notifications', 'telegramChatId', e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Alert Types</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Signal Alerts</Label>
                        <p className="text-sm text-gray-600">New trading signals</p>
                      </div>
                      <Switch
                        checked={settings.notifications?.signalAlerts || false}
                        onCheckedChange={(checked) => updateSetting('notifications', 'signalAlerts', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Target Hit Alerts</Label>
                        <p className="text-sm text-gray-600">When targets are reached</p>
                      </div>
                      <Switch
                        checked={settings.notifications?.targetHitAlerts || false}
                        onCheckedChange={(checked) => updateSetting('notifications', 'targetHitAlerts', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Stop Loss Alerts</Label>
                        <p className="text-sm text-gray-600">When stop losses are hit</p>
                      </div>
                      <Switch
                        checked={settings.notifications?.stopLossAlerts || false}
                        onCheckedChange={(checked) => updateSetting('notifications', 'stopLossAlerts', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>System Alerts</Label>
                        <p className="text-sm text-gray-600">System status updates</p>
                      </div>
                      <Switch
                        checked={settings.notifications?.systemAlerts || false}
                        onCheckedChange={(checked) => updateSetting('notifications', 'systemAlerts', checked)}
                      />
                    </div>
                  </div>

                  <h3 className="text-lg font-semibold">Reports</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Daily Reports</Label>
                        <p className="text-sm text-gray-600">Daily performance summary</p>
                      </div>
                      <Switch
                        checked={settings.notifications?.dailyReports || false}
                        onCheckedChange={(checked) => updateSetting('notifications', 'dailyReports', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Weekly Reports</Label>
                        <p className="text-sm text-gray-600">Weekly performance analysis</p>
                      </div>
                      <Switch
                        checked={settings.notifications?.weeklyReports || false}
                        onCheckedChange={(checked) => updateSetting('notifications', 'weeklyReports', checked)}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Trading Settings */}
          <TabsContent value="trading" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="h-5 w-5 mr-2" />
                  Trading Settings
                </CardTitle>
                <CardDescription>
                  Configure trading parameters and risk management
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="defaultStrategy">Default Strategy</Label>
                    <Select 
                      value={settings.trading?.defaultStrategy || ''} 
                      onValueChange={(value) => updateSetting('trading', 'defaultStrategy', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="multibagger">Multibagger</SelectItem>
                        <SelectItem value="momentum">Momentum</SelectItem>
                        <SelectItem value="swing">Swing Trading</SelectItem>
                        <SelectItem value="breakout">Breakout</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="minConfidence">Min Confidence (%)</Label>
                    <Input
                      id="minConfidence"
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={(settings.trading?.minConfidence || 0) * 100}
                      onChange={(e) => updateSetting('trading', 'minConfidence', parseFloat(e.target.value) / 100)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="maxPositions">Max Positions</Label>
                    <Input
                      id="maxPositions"
                      type="number"
                      min="1"
                      max="100"
                      value={settings.trading?.maxPositions || ''}
                      onChange={(e) => updateSetting('trading', 'maxPositions', parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="riskPerTrade">Risk Per Trade (%)</Label>
                    <Input
                      id="riskPerTrade"
                      type="number"
                      min="0.1"
                      max="10"
                      step="0.1"
                      value={settings.trading?.riskPerTrade || ''}
                      onChange={(e) => updateSetting('trading', 'riskPerTrade', parseFloat(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="stopLossPercent">Default Stop Loss (%)</Label>
                    <Input
                      id="stopLossPercent"
                      type="number"
                      min="1"
                      max="50"
                      step="0.1"
                      value={settings.trading?.stopLossPercent || ''}
                      onChange={(e) => updateSetting('trading', 'stopLossPercent', parseFloat(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="targetMultiplier">Target Multiplier</Label>
                    <Input
                      id="targetMultiplier"
                      type="number"
                      min="1"
                      max="10"
                      step="0.1"
                      value={settings.trading?.targetMultiplier || ''}
                      onChange={(e) => updateSetting('trading', 'targetMultiplier', parseFloat(e.target.value))}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Paper Trading Mode</Label>
                      <p className="text-sm text-gray-600">Practice trading without real money</p>
                    </div>
                    <Switch
                      checked={settings.trading?.paperTrading || false}
                      onCheckedChange={(checked) => updateSetting('trading', 'paperTrading', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Auto Execution</Label>
                      <p className="text-sm text-gray-600">Automatically execute trades</p>
                    </div>
                    <Switch
                      checked={settings.trading?.autoExecution || false}
                      onCheckedChange={(checked) => updateSetting('trading', 'autoExecution', checked)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* API Settings */}
          <TabsContent value="api" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="h-5 w-5 mr-2" />
                  API Settings
                </CardTitle>
                <CardDescription>
                  Configure API connections and parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="apiUrl">API URL</Label>
                    <Input
                      id="apiUrl"
                      value={settings.api?.apiUrl || ''}
                      onChange={(e) => updateSetting('api', 'apiUrl', e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timeout">Timeout (seconds)</Label>
                    <Input
                      id="timeout"
                      type="number"
                      min="5"
                      max="300"
                      value={settings.api?.timeout || ''}
                      onChange={(e) => updateSetting('api', 'timeout', parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="retryAttempts">Retry Attempts</Label>
                    <Input
                      id="retryAttempts"
                      type="number"
                      min="1"
                      max="10"
                      value={settings.api?.retryAttempts || ''}
                      onChange={(e) => updateSetting('api', 'retryAttempts', parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="rateLimitPerMinute">Rate Limit (per minute)</Label>
                    <Input
                      id="rateLimitPerMinute"
                      type="number"
                      min="1"
                      max="1000"
                      value={settings.api?.rateLimitPerMinute || ''}
                      onChange={(e) => updateSetting('api', 'rateLimitPerMinute', parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="apiKey">API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="apiKey"
                      type={showApiKey ? 'text' : 'password'}
                      value={settings.api?.apiKey || ''}
                      onChange={(e) => updateSetting('api', 'apiKey', e.target.value)}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Settings */}
          <TabsContent value="security" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="h-5 w-5 mr-2" />
                  Security Settings
                </CardTitle>
                <CardDescription>
                  Configure security and access control settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="sessionTimeout">Session Timeout (minutes)</Label>
                    <Input
                      id="sessionTimeout"
                      type="number"
                      min="5"
                      max="480"
                      value={settings.security?.sessionTimeout || ''}
                      onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="apiKeyRotation">API Key Rotation (days)</Label>
                    <Input
                      id="apiKeyRotation"
                      type="number"
                      min="1"
                      max="365"
                      value={settings.security?.apiKeyRotation || ''}
                      onChange={(e) => updateSetting('security', 'apiKeyRotation', parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ipWhitelist">IP Whitelist</Label>
                  <Textarea
                    id="ipWhitelist"
                    placeholder="Enter IP addresses, one per line"
                    value={settings.security?.ipWhitelist || ''}
                    onChange={(e) => updateSetting('security', 'ipWhitelist', e.target.value)}
                  />
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Two-Factor Authentication</Label>
                      <p className="text-sm text-gray-600">Enable 2FA for additional security</p>
                    </div>
                    <Switch
                      checked={settings.security?.twoFactorAuth || false}
                      onCheckedChange={(checked) => updateSetting('security', 'twoFactorAuth', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Audit Logging</Label>
                      <p className="text-sm text-gray-600">Log all system activities</p>
                    </div>
                    <Switch
                      checked={settings.security?.auditLogging || false}
                      onCheckedChange={(checked) => updateSetting('security', 'auditLogging', checked)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
