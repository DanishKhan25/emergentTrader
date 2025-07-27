'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

export default function PriceChart({ 
  data = [], 
  type = 'line', 
  height = 300, 
  showGrid = true,
  color = '#3B82F6',
  fillColor = '#3B82F610'
}) {
  // Mock price data if none provided
  const mockData = data.length > 0 ? data : [
    { date: '2024-08-01', price: 2234.56, volume: 1200000 },
    { date: '2024-09-01', price: 2267.89, volume: 1350000 },
    { date: '2024-10-01', price: 2298.45, volume: 1180000 },
    { date: '2024-11-01', price: 2356.78, volume: 1420000 },
    { date: '2024-12-01', price: 2398.45, volume: 1380000 },
    { date: '2025-01-01', price: 2456.75, volume: 1234567 }
  ]

  const formatPrice = (value) => {
    return `₹${value.toFixed(2)}`
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-IN', { 
      month: 'short', 
      day: 'numeric' 
    })
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{formatDate(label)}</p>
          <p className="text-blue-600">
            Price: {formatPrice(payload[0].value)}
          </p>
          {payload[1] && (
            <p className="text-gray-600">
              Volume: {payload[1].value.toLocaleString()}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  if (type === 'area') {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={mockData}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            stroke="#666"
            fontSize={12}
          />
          <YAxis 
            tickFormatter={formatPrice}
            stroke="#666"
            fontSize={12}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area 
            type="monotone" 
            dataKey="price" 
            stroke={color}
            fill={fillColor}
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={mockData}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
        <XAxis 
          dataKey="date" 
          tickFormatter={formatDate}
          stroke="#666"
          fontSize={12}
        />
        <YAxis 
          tickFormatter={formatPrice}
          stroke="#666"
          fontSize={12}
        />
        <Tooltip content={<CustomTooltip />} />
        <Line 
          type="monotone" 
          dataKey="price" 
          stroke={color}
          strokeWidth={2}
          dot={{ fill: color, strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6, stroke: color, strokeWidth: 2 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
