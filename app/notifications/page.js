'use client'

import MainLayout from '@/components/layout/MainLayout'
import NotificationPanel from '@/components/notifications/NotificationPanel'

export default function NotificationsPage() {
  return (
    <MainLayout>
      <div className="container mx-auto p-6">
        <NotificationPanel />
      </div>
    </MainLayout>
  )
}
