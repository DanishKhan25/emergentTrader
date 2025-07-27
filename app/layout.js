import './globals.css'
import { Inter } from 'next/font/google'

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
        <div className="min-h-full">
          {children}
        </div>
      </body>
    </html>
  )
}