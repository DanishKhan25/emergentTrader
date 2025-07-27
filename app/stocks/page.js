'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Search, 
  Filter, 
  TrendingUp, 
  TrendingDown, 
  Database,
  RefreshCw,
  Star,
  CheckCircle
} from 'lucide-react'

export default function StocksPage() {
  const [stocks, setStocks] = useState([])
  const [shariahStocks, setShariahStocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('all')

  // Mock data for demonstration
  const mockStocks = [
    {
      symbol: 'RELIANCE',
      name: 'Reliance Industries Ltd',
      price: 2456.75,
      change: 23.45,
      changePercent: 0.96,
      volume: 1234567,
      marketCap: 1658900000000,
      pe: 24.5,
      isShariahCompliant: true
    },
    {
      symbol: 'TCS',
      name: 'Tata Consultancy Services',
      price: 3789.20,
      change: -45.30,
      changePercent: -1.18,
      volume: 987654,
      marketCap: 1389000000000,
      pe: 28.7,
      isShariahCompliant: true
    },
    {
      symbol: 'HDFCBANK',
      name: 'HDFC Bank Limited',
      price: 1678.90,
      change: 12.35,
      changePercent: 0.74,
      volume: 2345678,
      marketCap: 1245000000000,
      pe: 19.2,
      isShariahCompliant: false
    },
    {
      symbol: 'INFY',
      name: 'Infosys Limited',
      price: 1456.30,
      change: 8.75,
      changePercent: 0.60,
      volume: 1876543,
      marketCap: 612000000000,
      pe: 22.1,
      isShariahCompliant: true
    },
    {
      symbol: 'ICICIBANK',
      name: 'ICICI Bank Limited',
      price: 1123.45,
      change: -15.60,
      changePercent: -1.37,
      volume: 3456789,
      marketCap: 789000000000,
      pe: 16.8,
      isShariahCompliant: false
    }
  ]

  useEffect(() => {
    // Simulate API call
    setLoading(true)
    setTimeout(() => {
      setStocks(mockStocks)
      setShariahStocks(mockStocks.filter(stock => stock.isShariahCompliant))
      setLoading(false)
    }, 1000)
  }, [])

  const filteredStocks = (stockList) => {
    return stockList.filter(stock =>
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatMarketCap = (value) => {
    if (value >= 1e12) return `₹${(value / 1e12).toFixed(2)}T`
    if (value >= 1e9) return `₹${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `₹${(value / 1e6).toFixed(2)}M`
    return `₹${value}`
  }

  const StockCard = ({ stock }) => (
    <Card className="hover:shadow-md transition-shadow cursor-pointer">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Database className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{stock.symbol}</h3>
              <p className="text-sm text-gray-600 truncate max-w-48">{stock.name}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {stock.isShariahCompliant && (
              <Badge variant="secondary" className="text-green-700 bg-green-100">
                <CheckCircle className="h-3 w-3 mr-1" />
                Shariah
              </Badge>
            )}
            <Button variant="ghost" size="sm">
              <Star className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-2xl font-bold">{formatCurrency(stock.price)}</p>
            <div className="flex items-center space-x-1">
              {stock.change >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-500" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-sm font-medium ${
                stock.change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
              </span>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-600">Market Cap</p>
            <p className="font-semibold">{formatMarketCap(stock.marketCap)}</p>
            <p className="text-sm text-gray-600 mt-1">P/E: {stock.pe}</p>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Volume: {stock.volume.toLocaleString()}</span>
            <Button variant="outline" size="sm">
              View Details
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <MainLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Stock Universe</h1>
          <p className="text-gray-600 mt-2">
            Explore and analyze stocks from the NSE universe with real-time data and Shariah compliance filtering.
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search stocks by symbol or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex space-x-2">
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
            <Button variant="outline" onClick={() => setLoading(true)}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="all">All Stocks ({stocks.length})</TabsTrigger>
            <TabsTrigger value="shariah">Shariah ({shariahStocks.length})</TabsTrigger>
            <TabsTrigger value="watchlist">Watchlist (0)</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} className="animate-pulse">
                    <CardContent className="p-6">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                      <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredStocks(stocks).map((stock) => (
                  <StockCard key={stock.symbol} stock={stock} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="shariah" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredStocks(shariahStocks).map((stock) => (
                <StockCard key={stock.symbol} stock={stock} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="watchlist" className="mt-6">
            <Card>
              <CardContent className="p-12 text-center">
                <Star className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No stocks in watchlist</h3>
                <p className="text-gray-600 mb-4">Add stocks to your watchlist to track them easily.</p>
                <Button>Browse Stocks</Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
