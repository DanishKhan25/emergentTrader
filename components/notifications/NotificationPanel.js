'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { 
  Bell, 
  Search, 
  Filter, 
  Settings, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Target,
  DollarSign,
  TrendingUp,
  Info,
  Trash2,
  CheckCheck,
  Volume2,
  VolumeX
} from 'lucide-react'
import { useNotifications } from './NotificationProvider'

export default function NotificationPanel() {
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('newest')
  const [notificationSettings, setNotificationSettings] = useState({
    signals: true,
    trades: true,
    portfolio: true,
    alerts: true,
    sound: true,
    desktop: true,
    email: false
  })

  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    notificationTypes
  } = useNotifications()

  // Filter and sort notifications
  const filteredNotifications = notifications
    .filter(notification => {
      if (filter === 'unread' && notification.read) return false
      if (filter !== 'all' && notification.type !== filter) return false
      if (searchTerm && !notification.title.toLowerCase().includes(searchTerm.toLowerCase()) && 
          !notification.message.toLowerCase().includes(searchTerm.toLowerCase())) return false
      return true
    })
    .sort((a, b) => {
      if (sortBy === 'newest') return new Date(b.timestamp) - new Date(a.timestamp)
      if (sortBy === 'oldest') return new Date(a.timestamp) - new Date(b.timestamp)
      if (sortBy === 'unread') return a.read - b.read
      return 0
    })

  const formatDateTime = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getNotificationStats = () => {
    const stats = {
      total: notifications.length,
      unread: unreadCount,
      signals: notifications.filter(n => n.type === 'signal').length,
      trades: notifications.filter(n => n.type === 'trade').length,
      portfolio: notifications.filter(n => n.type === 'portfolio').length,
      alerts: notifications.filter(n => n.type === 'alert').length
    }
    return stats
  }

  const stats = getNotificationStats()

  const handleSettingChange = (setting, value) => {
    setNotificationSettings(prev => ({
      ...prev,
      [setting]: value
    }))
    // Here you would typically save to backend/localStorage
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-gray-600 mt-1">Manage your trading alerts and updates</p>
        </div>
        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <Button onClick={markAllAsRead} variant="outline">
              <CheckCheck className="h-4 w-4 mr-2" />
              Mark all read
            </Button>
          )}
          <Button onClick={clearAll} variant="outline" className="text-red-600 hover:text-red-700">
            <Trash2 className="h-4 w-4 mr-2" />
            Clear all
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{stats.unread}</div>
              <div className="text-sm text-gray-600">Unread</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.signals}</div>
              <div className="text-sm text-gray-600">Signals</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.trades}</div>
              <div className="text-sm text-gray-600">Trades</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">{stats.portfolio}</div>
              <div className="text-sm text-gray-600">Portfolio</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.alerts}</div>
              <div className="text-sm text-gray-600">Alerts</div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="notifications" className="space-y-6">
        <TabsList>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search notifications..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select value={filter} onValueChange={setFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="unread">Unread Only</SelectItem>
                    <SelectItem value="signal">Signals</SelectItem>
                    <SelectItem value="trade">Trades</SelectItem>
                    <SelectItem value="portfolio">Portfolio</SelectItem>
                    <SelectItem value="alert">Alerts</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="newest">Newest</SelectItem>
                    <SelectItem value="oldest">Oldest</SelectItem>
                    <SelectItem value="unread">Unread First</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Notifications List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notifications ({filteredNotifications.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {filteredNotifications.length === 0 ? (
                <div className="text-center py-12">
                  <Bell className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">No notifications found</h3>
                  <p className="text-gray-500">
                    {searchTerm || filter !== 'all' 
                      ? 'Try adjusting your filters or search terms'
                      : 'You\'ll see trading signals and updates here'
                    }
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredNotifications.map((notification) => {
                    const config = notificationTypes[notification.type] || notificationTypes.info
                    const Icon = config.icon

                    return (
                      <div
                        key={notification.id}
                        className={`p-4 border rounded-lg hover:bg-gray-50 transition-colors ${
                          !notification.read ? 'bg-blue-50/50 border-blue-200' : 'border-gray-200'
                        }`}
                      >
                        <div className="flex items-start gap-4">
                          {/* Icon */}
                          <div className={`flex-shrink-0 w-10 h-10 rounded-full ${config.bgColor} ${config.borderColor} border flex items-center justify-center`}>
                            <Icon className={`h-5 w-5 ${config.color}`} />
                          </div>

                          {/* Content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <h4 className={`font-medium ${!notification.read ? 'text-gray-900' : 'text-gray-700'}`}>
                                    {notification.title}
                                  </h4>
                                  {!notification.read && (
                                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                                  )}
                                  <Badge variant="secondary" className="text-xs">
                                    {notification.type}
                                  </Badge>
                                </div>
                                <p className={`text-sm mb-2 ${!notification.read ? 'text-gray-700' : 'text-gray-500'}`}>
                                  {notification.message}
                                </p>
                                <p className="text-xs text-gray-400">
                                  {formatDateTime(notification.timestamp)}
                                </p>
                              </div>

                              {/* Actions */}
                              <div className="flex items-center gap-2 ml-4">
                                {!notification.read && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => markAsRead(notification.id)}
                                    className="text-xs"
                                  >
                                    <CheckCircle className="h-3 w-3 mr-1" />
                                    Mark read
                                  </Button>
                                )}
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => removeNotification(notification.id)}
                                  className="text-xs text-red-600 hover:text-red-700"
                                >
                                  <XCircle className="h-3 w-3 mr-1" />
                                  Remove
                                </Button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Notification Settings
              </CardTitle>
              <CardDescription>
                Configure which notifications you want to receive and how
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Notification Types */}
              <div>
                <h4 className="font-semibold mb-4">Notification Types</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Target className="h-5 w-5 text-blue-600" />
                      <div>
                        <Label htmlFor="signals">Trading Signals</Label>
                        <p className="text-sm text-gray-500">New buy/sell signals and recommendations</p>
                      </div>
                    </div>
                    <Switch
                      id="signals"
                      checked={notificationSettings.signals}
                      onCheckedChange={(checked) => handleSettingChange('signals', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <DollarSign className="h-5 w-5 text-green-600" />
                      <div>
                        <Label htmlFor="trades">Trade Executions</Label>
                        <p className="text-sm text-gray-500">Buy and sell order confirmations</p>
                      </div>
                    </div>
                    <Switch
                      id="trades"
                      checked={notificationSettings.trades}
                      onCheckedChange={(checked) => handleSettingChange('trades', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="h-5 w-5 text-purple-600" />
                      <div>
                        <Label htmlFor="portfolio">Portfolio Updates</Label>
                        <p className="text-sm text-gray-500">Portfolio performance and value changes</p>
                      </div>
                    </div>
                    <Switch
                      id="portfolio"
                      checked={notificationSettings.portfolio}
                      onCheckedChange={(checked) => handleSettingChange('portfolio', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <AlertTriangle className="h-5 w-5 text-orange-600" />
                      <div>
                        <Label htmlFor="alerts">Price Alerts</Label>
                        <p className="text-sm text-gray-500">Target hits, stop losses, and price movements</p>
                      </div>
                    </div>
                    <Switch
                      id="alerts"
                      checked={notificationSettings.alerts}
                      onCheckedChange={(checked) => handleSettingChange('alerts', checked)}
                    />
                  </div>
                </div>
              </div>

              {/* Delivery Methods */}
              <div>
                <h4 className="font-semibold mb-4">Delivery Methods</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {notificationSettings.sound ? (
                        <Volume2 className="h-5 w-5 text-blue-600" />
                      ) : (
                        <VolumeX className="h-5 w-5 text-gray-400" />
                      )}
                      <div>
                        <Label htmlFor="sound">Sound Notifications</Label>
                        <p className="text-sm text-gray-500">Play sound for important notifications</p>
                      </div>
                    </div>
                    <Switch
                      id="sound"
                      checked={notificationSettings.sound}
                      onCheckedChange={(checked) => handleSettingChange('sound', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Bell className="h-5 w-5 text-green-600" />
                      <div>
                        <Label htmlFor="desktop">Desktop Notifications</Label>
                        <p className="text-sm text-gray-500">Show browser notifications</p>
                      </div>
                    </div>
                    <Switch
                      id="desktop"
                      checked={notificationSettings.desktop}
                      onCheckedChange={(checked) => handleSettingChange('desktop', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Info className="h-5 w-5 text-purple-600" />
                      <div>
                        <Label htmlFor="email">Email Notifications</Label>
                        <p className="text-sm text-gray-500">Send important alerts via email</p>
                      </div>
                    </div>
                    <Switch
                      id="email"
                      checked={notificationSettings.email}
                      onCheckedChange={(checked) => handleSettingChange('email', checked)}
                    />
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
