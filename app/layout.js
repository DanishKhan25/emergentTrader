import './globals.css'
import { Inter } from 'next/font/google'
import { DataProvider } from '@/contexts/DataContext'
import AuthProvider from '@/contexts/AuthContext'
import WebSocketProvider from '@/contexts/WebSocketContext'
import NotificationProvider from '@/components/notifications/NotificationProvider'
import { Toaster } from 'sonner'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'EmergentTrader - AI-Powered Trading Signals',
  description: 'Professional trading signal platform with 87% success rate and ML-enhanced multibagger strategies',
  keywords: 'trading, signals, AI, machine learning, stocks, NSE, multibagger, Shariah compliant',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50 antialiased`}>
        <AuthProvider>
          <DataProvider>
            <NotificationProvider>
              <WebSocketProvider>
                <div className="min-h-full">
                  {children}
                </div>
                <Toaster 
                  position="top-right"
                  richColors
                  closeButton
                  duration={5000}
                />
              </WebSocketProvider>
            </NotificationProvider>
          </DataProvider>
        </AuthProvider>
      </body>
    </html>
  )
}