'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

export default function ProtectedRoute({ children, requiredRole = null }) {
  const { user, loading, isAuthenticated, hasRole } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (!isAuthenticated()) {
        router.push('/login')
        return
      }

      if (requiredRole && !hasRole(requiredRole)) {
        router.push('/unauthorized')
        return
      }
    }
  }, [user, loading, isAuthenticated, hasRole, requiredRole, router])

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Show nothing while redirecting
  if (!isAuthenticated() || (requiredRole && !hasRole(requiredRole))) {
    return null
  }

  // Render children if authenticated and authorized
  return children
}
