import { useState, useEffect, useCallback } from 'react'
import apiService from '@/lib/api'

export function usePortfolio() {
  const [portfolio, setPortfolio] = useState(null)
  const [positions, setPositions] = useState([])
  const [allocation, setAllocation] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchPortfolioData = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Fetch all portfolio data concurrently
      const [portfolioResult, positionsResult, allocationResult] = await Promise.allSettled([
        apiService.getPortfolioOverview(),
        apiService.getPortfolioPositions(),
        apiService.getPortfolioAllocation()
      ])

      // Handle portfolio overview
      if (portfolioResult.status === 'fulfilled' && portfolioResult.value.success) {
        setPortfolio(portfolioResult.value.data)
      } else {
        console.warn('Failed to fetch portfolio overview:', portfolioResult.reason)
        setPortfolio(null)
      }

      // Handle positions
      if (positionsResult.status === 'fulfilled' && positionsResult.value.success) {
        setPositions(positionsResult.value.data || [])
      } else {
        console.warn('Failed to fetch positions:', positionsResult.reason)
        setPositions([])
      }

      // Handle allocation
      if (allocationResult.status === 'fulfilled' && allocationResult.value.success) {
        setAllocation(allocationResult.value.data || [])
      } else {
        console.warn('Failed to fetch allocation:', allocationResult.reason)
        setAllocation([])
      }

      // If all requests failed, show error
      if (
        portfolioResult.status === 'rejected' && 
        positionsResult.status === 'rejected' && 
        allocationResult.status === 'rejected'
      ) {
        throw new Error('Failed to fetch portfolio data from all endpoints')
      }

      setLastUpdated(new Date())

    } catch (err) {
      console.error('Error fetching portfolio data:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const refreshData = useCallback(() => {
    fetchPortfolioData()
  }, [fetchPortfolioData])

  // Auto-refresh every 30 seconds
  useEffect(() => {
    fetchPortfolioData()
    
    const interval = setInterval(() => {
      fetchPortfolioData()
    }, 30000)

    return () => clearInterval(interval)
  }, [fetchPortfolioData])

  // Calculate derived metrics
  const metrics = {
    totalValue: portfolio?.totalValue || 0,
    totalInvested: portfolio?.totalInvested || 0,
    totalPnL: portfolio?.totalPnL || 0,
    totalPnLPercent: portfolio?.totalPnLPercent || 0,
    activePositionsCount: positions.length,
    profitablePositions: positions.filter(p => p.pnl > 0).length,
    losingPositions: positions.filter(p => p.pnl < 0).length,
    winRate: positions.length > 0 ? (positions.filter(p => p.pnl > 0).length / positions.length * 100) : 0
  }

  return {
    portfolio,
    positions,
    allocation,
    loading,
    error,
    lastUpdated,
    metrics,
    refreshData,
    isStale: lastUpdated && (Date.now() - lastUpdated.getTime()) > 60000 // 1 minute
  }
}

export default usePortfolio
