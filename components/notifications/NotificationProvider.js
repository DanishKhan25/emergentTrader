"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { toast } from "sonner";
import {
  Bell,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Info,
  TrendingUp,
  Target,
  DollarSign,
} from "lucide-react";

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error(
      "useNotifications must be used within a NotificationProvider"
    );
  }
  return context;
};

export default function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Notification types with their configurations
  const notificationTypes = {
    signal: {
      icon: Target,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
    },
    trade: {
      icon: DollarSign,
      color: "text-green-600",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
    },
    portfolio: {
      icon: TrendingUp,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      borderColor: "border-purple-200",
    },
    alert: {
      icon: AlertTriangle,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      borderColor: "border-orange-200",
    },
    success: {
      icon: CheckCircle,
      color: "text-green-600",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
    },
    error: {
      icon: XCircle,
      color: "text-red-600",
      bgColor: "bg-red-50",
      borderColor: "border-red-200",
    },
    info: {
      icon: Info,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
    },
  };

  // Add notification function
  const addNotification = (notification) => {
    const id = Date.now().toString();
    const newNotification = {
      id,
      timestamp: new Date().toISOString(),
      read: false,
      ...notification,
    };

    setNotifications((prev) => [newNotification, ...prev]);
    setUnreadCount((prev) => prev + 1);

    // Show toast notification
    const config =
      notificationTypes[notification.type] || notificationTypes.info;
    const Icon = config.icon;

    toast(notification.title, {
      description: notification.message,
      icon: <Icon className="h-4 w-4" />,
      duration: notification.duration || 5000,
      action: notification.action
        ? {
            label: notification.action.label,
            onClick: notification.action.onClick,
          }
        : undefined,
    });

    return id;
  };

  // Mark notification as read
  const markAsRead = (id) => {
    setNotifications((prev) =>
      prev.map((notif) => (notif.id === id ? { ...notif, read: true } : notif))
    );
    setUnreadCount((prev) => Math.max(0, prev - 1));
  };

  // Mark all as read
  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((notif) => ({ ...notif, read: true })));
    setUnreadCount(0);
  };

  // Remove notification
  const removeNotification = (id) => {
    setNotifications((prev) => {
      const notification = prev.find((n) => n.id === id);
      if (notification && !notification.read) {
        setUnreadCount((count) => Math.max(0, count - 1));
      }
      return prev.filter((n) => n.id !== id);
    });
  };

  // Clear all notifications
  const clearAll = () => {
    setNotifications([]);
    setUnreadCount(0);
  };

  // Predefined notification functions for common scenarios
  const notifySignalGenerated = (signal) => {
    return addNotification({
      type: "signal",
      title: "New Trading Signal",
      message: `${signal.strategy} signal for ${signal.symbol} - ${(
        signal.confidence * 100
      ).toFixed(0)}% confidence`,
      data: signal,
      action: {
        label: "View Signal",
        onClick: () => (window.location.href = `/signals`),
      },
    });
  };

  const notifyTradeExecuted = (trade) => {
    return addNotification({
      type: "trade",
      title: "Trade Executed",
      message: `${trade.type} ${trade.quantity} shares of ${trade.symbol} at ₹${trade.price}`,
      data: trade,
      action: {
        label: "View Portfolio",
        onClick: () => (window.location.href = `/portfolio`),
      },
    });
  };

  const notifyPortfolioUpdate = (update) => {
    return addNotification({
      type: "portfolio",
      title: "Portfolio Update",
      message: update.message,
      data: update,
      action: {
        label: "View Portfolio",
        onClick: () => (window.location.href = `/portfolio`),
      },
    });
  };

  const notifyPriceAlert = (alert) => {
    return addNotification({
      type: "alert",
      title: "Price Alert",
      message: `${alert.symbol} has ${alert.direction} ₹${alert.price} (${alert.change}%)`,
      data: alert,
      duration: 8000,
      action: {
        label: "View Stock",
        onClick: () => (window.location.href = `/stocks/${alert.symbol}`),
      },
    });
  };

  const notifyTargetHit = (position) => {
    return addNotification({
      type: "success",
      title: "Target Hit! 🎯",
      message: `${position.symbol} reached target price of ₹${position.targetPrice}`,
      data: position,
      duration: 10000,
      action: {
        label: "Sell Position",
        onClick: () => (window.location.href = `/portfolio`),
      },
    });
  };

  const notifyStopLoss = (position) => {
    return addNotification({
      type: "error",
      title: "Stop Loss Triggered",
      message: `${position.symbol} hit stop loss at ₹${position.stopLoss}`,
      data: position,
      duration: 10000,
      action: {
        label: "Review Position",
        onClick: () => (window.location.href = `/portfolio`),
      },
    });
  };

  // Listen for real WebSocket notifications
  useEffect(() => {
    // Real-time WebSocket integration for notifications
    const handleWebSocketMessage = (data) => {
      switch (data.type) {
        case 'signal_generated':
          notifySignalGenerated(data.data)
          break
        case 'target_hit':
          notifyTargetHit(data.data)
          break
        case 'stop_loss_hit':
          notifyStopLoss(data.data)
          break
        case 'portfolio_update':
          notifyPortfolioUpdate(data.data)
          break
        case 'system_alert':
          addNotification({
            type: data.data.type || 'info',
            title: data.data.title || 'System Alert',
            message: data.data.message,
            duration: data.data.duration || 5000
          })
          break
        default:
          // Handle other notification types
          if (data.notification) {
            addNotification(data.notification)
          }
          break
      }
    }

    // This will be handled by the WebSocket context
    // The WebSocket context will call notification functions directly
    // No simulation needed - real notifications come from backend
    
    return () => {
      // Cleanup if needed
    }
  }, []);

  const value = {
    notifications,
    unreadCount,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    // Predefined notification functions
    notifySignalGenerated,
    notifyTradeExecuted,
    notifyPortfolioUpdate,
    notifyPriceAlert,
    notifyTargetHit,
    notifyStopLoss,
    // Notification types for styling
    notificationTypes,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}
