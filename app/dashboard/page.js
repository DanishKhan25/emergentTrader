import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DynamicDashboard from '@/components/DynamicDashboard'

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DynamicDashboard />
    </ProtectedRoute>
  )
}
