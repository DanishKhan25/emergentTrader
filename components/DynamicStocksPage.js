'use client'

import { useState, useEffect, useMemo } from 'react'
import { useData } from '@/contexts/DataContext'
import MainLayout from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { 
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  Star,
  StarOff,
  RefreshCw,
  CheckCircle,
  BarChart3,
  DollarSign,
  Percent,
  Activity
} from 'lucide-react'
import Link from 'next/link'

export default function DynamicStocksPage() {
  const {
    stocks,
    shariahStocks,
    isLoading,
    error,
    settings,
    refreshData,
    updateSettings
  } = useData()

  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('symbol')
  const [sortOrder, setSortOrder] = useState('asc')
  const [sectorFilter, setSectorFilter] = useState('all')
  const [priceRange, setPriceRange] = useState('all')
  const [watchlist, setWatchlist] = useState(new Set())

  // Get current stock list based on Shariah filter
  const currentStocks = settings.shariahOnly ? shariahStocks : stocks

  // Extract unique sectors for filtering
  const sectors = useMemo(() => {
    const sectorSet = new Set()
    currentStocks.forEach(stock => {
      if (stock.sector) sectorSet.add(stock.sector)
    })
    return Array.from(sectorSet).sort()
  }, [currentStocks])

  // Filter and sort stocks
  const filteredStocks = useMemo(() => {
    let filtered = currentStocks.filter(stock => {
      // Search filter
      const matchesSearch = !searchTerm || 
        stock.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.name?.toLowerCase().includes(searchTerm.toLowerCase())

      // Sector filter
      const matchesSector = sectorFilter === 'all' || stock.sector === sectorFilter

      // Price range filter
      let matchesPrice = true
      if (priceRange !== 'all' && stock.price) {
        switch (priceRange) {
          case 'under-100':
            matchesPrice = stock.price < 100
            break
          case '100-500':
            matchesPrice = stock.price >= 100 && stock.price < 500
            break
          case '500-1000':
            matchesPrice = stock.price >= 500 && stock.price < 1000
            break
          case 'over-1000':
            matchesPrice = stock.price >= 1000
            break
        }
      }

      return matchesSearch && matchesSector && matchesPrice
    })

    // Sort stocks
    filtered.sort((a, b) => {
      let aValue = a[sortBy] || 0
      let bValue = b[sortBy] || 0

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    return filtered
  }, [currentStocks, searchTerm, sectorFilter, priceRange, sortBy, sortOrder])

  // Toggle watchlist
  const toggleWatchlist = (symbol) => {
    const newWatchlist = new Set(watchlist)
    if (newWatchlist.has(symbol)) {
      newWatchlist.delete(symbol)
    } else {
      newWatchlist.add(symbol)
    }
    setWatchlist(newWatchlist)
    
    // Save to localStorage
    localStorage.setItem('emergentTrader_watchlist', JSON.stringify(Array.from(newWatchlist)))
  }

  // Load watchlist from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('emergentTrader_watchlist')
      if (saved) {
        setWatchlist(new Set(JSON.parse(saved)))
      }
    } catch (error) {
      console.warn('Failed to load watchlist:', error)
    }
  }, [])

  // Format currency
  const formatCurrency = (value) => {
    if (!value) return '₹0.00'
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(value)
  }

  // Format percentage
  const formatPercentage = (value) => {
    if (!value) return '0.00%'
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  // Render stock card
  const renderStockCard = (stock) => (
    <Card key={stock.symbol} className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <h3 className="font-bold text-lg">{stock.symbol}</h3>
              {stock.isShariahCompliant && (
                <Badge variant="secondary" className="text-green-700 bg-green-100">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Shariah
                </Badge>
              )}
            </div>
            <p className="text-gray-600 text-sm mb-1">{stock.name}</p>
            <p className="text-gray-500 text-xs">{stock.sector}</p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleWatchlist(stock.symbol)}
          >
            {watchlist.has(stock.symbol) ? (
              <Star className="h-4 w-4 fill-current text-yellow-500" />
            ) : (
              <StarOff className="h-4 w-4" />
            )}
          </Button>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600">Current Price</p>
            <p className="font-bold text-lg">{formatCurrency(stock.price)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Change</p>
            <div className="flex items-center">
              {(stock.change || 0) >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
              )}
              <span className={`font-bold ${(stock.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPercentage(stock.changePercent)}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 text-xs text-gray-600 mb-4">
          <div>
            <span className="block">P/E</span>
            <span className="font-medium">{stock.pe || 'N/A'}</span>
          </div>
          <div>
            <span className="block">Market Cap</span>
            <span className="font-medium">
              {stock.marketCap ? `₹${(stock.marketCap / 1e9).toFixed(1)}B` : 'N/A'}
            </span>
          </div>
          <div>
            <span className="block">Volume</span>
            <span className="font-medium">
              {stock.volume ? `${(stock.volume / 1000).toFixed(0)}K` : 'N/A'}
            </span>
          </div>
        </div>

        <div className="flex space-x-2">
          <Link href={`/stocks/${stock.symbol}`} className="flex-1">
            <Button variant="outline" className="w-full">
              <BarChart3 className="h-4 w-4 mr-2" />
              View Details
            </Button>
          </Link>
          <Button size="sm" className="px-3">
            <Activity className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <MainLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Live Stock Universe</h1>
            <p className="text-gray-600 mt-1">
              Real-time data for {filteredStocks.length} stocks
              {settings.shariahOnly && ' (Shariah compliant only)'}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Switch
                checked={settings.shariahOnly}
                onCheckedChange={(checked) => updateSettings({ shariahOnly: checked })}
              />
              <span className="text-sm text-gray-600">Shariah Only</span>
            </div>
            <Button 
              variant="outline" 
              onClick={() => refreshData(['stocks'])}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Filters & Search</CardTitle>
            <CardDescription>Find stocks using real-time filters</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search stocks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Sector Filter */}
              <Select value={sectorFilter} onValueChange={setSectorFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Sectors" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sectors</SelectItem>
                  {sectors.map(sector => (
                    <SelectItem key={sector} value={sector}>{sector}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Price Range */}
              <Select value={priceRange} onValueChange={setPriceRange}>
                <SelectTrigger>
                  <SelectValue placeholder="All Prices" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Prices</SelectItem>
                  <SelectItem value="under-100">Under ₹100</SelectItem>
                  <SelectItem value="100-500">₹100 - ₹500</SelectItem>
                  <SelectItem value="500-1000">₹500 - ₹1000</SelectItem>
                  <SelectItem value="over-1000">Over ₹1000</SelectItem>
                </SelectContent>
              </Select>

              {/* Sort By */}
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger>
                  <SelectValue placeholder="Sort By" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="symbol">Symbol</SelectItem>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="price">Price</SelectItem>
                  <SelectItem value="changePercent">Change %</SelectItem>
                  <SelectItem value="marketCap">Market Cap</SelectItem>
                  <SelectItem value="volume">Volume</SelectItem>
                </SelectContent>
              </Select>

              {/* Sort Order */}
              <Select value={sortOrder} onValueChange={setSortOrder}>
                <SelectTrigger>
                  <SelectValue placeholder="Order" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="asc">Ascending</SelectItem>
                  <SelectItem value="desc">Descending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-600">Total Stocks</p>
              <p className="text-2xl font-bold">{currentStocks.length}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-600">Filtered Results</p>
              <p className="text-2xl font-bold text-blue-600">{filteredStocks.length}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-600">Watchlist</p>
              <p className="text-2xl font-bold text-yellow-600">{watchlist.size}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-sm text-gray-600">Shariah Stocks</p>
              <p className="text-2xl font-bold text-green-600">{shariahStocks.length}</p>
            </CardContent>
          </Card>
        </div>

        {/* Stock Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(9)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="h-8 bg-gray-200 rounded"></div>
                    <div className="h-8 bg-gray-200 rounded"></div>
                  </div>
                  <div className="h-10 bg-gray-200 rounded"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredStocks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredStocks.map(renderStockCard)}
          </div>
        ) : (
          <Card>
            <CardContent className="p-12 text-center">
              <Filter className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No stocks found</h3>
              <p className="text-gray-600 mb-4">
                Try adjusting your filters or search terms
              </p>
              <Button onClick={() => {
                setSearchTerm('')
                setSectorFilter('all')
                setPriceRange('all')
              }}>
                Clear Filters
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  )
}
