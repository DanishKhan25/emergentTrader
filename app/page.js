import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DynamicDashboard from '@/components/DynamicDashboard'

export default function Home() {
  return (
    <ProtectedRoute>
      <DynamicDashboard />
    </ProtectedRoute>
  )
}
