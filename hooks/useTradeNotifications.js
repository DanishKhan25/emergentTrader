'use client'

import { useNotifications } from '@/components/notifications/NotificationProvider'

export function useTradeNotifications() {
  const {
    notifySignalGenerated,
    notifyTradeExecuted,
    notifyPortfolioUpdate,
    notifyPriceAlert,
    notifyTargetHit,
    notifyStopLoss,
    addNotification
  } = useNotifications()

  // Notify when a new signal is generated
  const notifyNewSignal = async (signal) => {
    // Send to backend
    try {
      await fetch('http://localhost:8000/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'signal',
          title: 'New Trading Signal',
          message: `${signal.strategy} signal for ${signal.symbol} - ${(signal.confidence * 100).toFixed(0)}% confidence`,
          data: signal
        })
      })
    } catch (error) {
      console.error('Failed to send notification to backend:', error)
    }

    // Show local notification
    return notifySignalGenerated(signal)
  }

  // Notify when a trade is executed
  const notifyTradeComplete = async (trade) => {
    try {
      await fetch('http://localhost:8000/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'trade',
          title: 'Trade Executed',
          message: `${trade.type} ${trade.quantity} shares of ${trade.symbol} at ₹${trade.price}`,
          data: trade
        })
      })
    } catch (error) {
      console.error('Failed to send notification to backend:', error)
    }

    return notifyTradeExecuted(trade)
  }

  // Notify portfolio changes
  const notifyPortfolioChange = async (update) => {
    try {
      await fetch('http://localhost:8000/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'portfolio',
          title: 'Portfolio Update',
          message: update.message,
          data: update
        })
      })
    } catch (error) {
      console.error('Failed to send notification to backend:', error)
    }

    return notifyPortfolioUpdate(update)
  }

  // Notify price alerts
  const notifyPriceChange = async (alert) => {
    try {
      await fetch('http://localhost:8000/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'alert',
          title: 'Price Alert',
          message: `${alert.symbol} has ${alert.direction} ₹${alert.price} (${alert.change}%)`,
          data: alert
        })
      })
    } catch (error) {
      console.error('Failed to send notification to backend:', error)
    }

    return notifyPriceAlert(alert)
  }

  // Notify target hit
  const notifyTargetReached = async (position) => {
    try {
      await fetch('http://localhost:8000/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'success',
          title: 'Target Hit! 🎯',
          message: `${position.symbol} reached target price of ₹${position.targetPrice}`,
          data: position
        })
      })
    } catch (error) {
      console.error('Failed to send notification to backend:', error)
    }

    return notifyTargetHit(position)
  }

  // Notify stop loss
  const notifyStopLossHit = async (position) => {
    try {
      await fetch('http://localhost:8000/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'error',
          title: 'Stop Loss Triggered',
          message: `${position.symbol} hit stop loss at ₹${position.stopLoss}`,
          data: position
        })
      })
    } catch (error) {
      console.error('Failed to send notification to backend:', error)
    }

    return notifyStopLoss(position)
  }

  // Generic notification sender
  const sendNotification = async (notification) => {
    try {
      await fetch('http://localhost:8000/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(notification)
      })
    } catch (error) {
      console.error('Failed to send notification to backend:', error)
    }

    return addNotification(notification)
  }

  return {
    notifyNewSignal,
    notifyTradeComplete,
    notifyPortfolioChange,
    notifyPriceChange,
    notifyTargetReached,
    notifyStopLossHit,
    sendNotification
  }
}
