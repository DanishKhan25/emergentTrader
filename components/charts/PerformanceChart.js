'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function PerformanceChart({ 
  data = [], 
  type = 'bar', 
  height = 300,
  colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
}) {
  // Mock performance data if none provided
  const mockBarData = data.length > 0 ? data : [
    { name: 'Multibagger', value: 87.2, returns: 1828 },
    { name: 'Momentum', value: 73.2, returns: 24.5 },
    { name: 'Swing', value: 68.1, returns: 12.8 },
    { name: 'Breakout', value: 71.2, returns: 18.9 },
    { name: 'Value', value: 65.4, returns: 15.3 }
  ]

  const mockPieData = data.length > 0 ? data : [
    { name: 'Multibagger', value: 50.3, amount: 1234567 },
    { name: 'Momentum', value: 26.6, amount: 654321 },
    { name: 'Swing', value: 14.1, amount: 345678 },
    { name: 'Breakout', value: 9.0, amount: 222223 }
  ]

  const formatPercent = (value) => `${value.toFixed(1)}%`
  
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const CustomBarTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{label}</p>
          <p className="text-blue-600">
            Success Rate: {formatPercent(payload[0].value)}
          </p>
          <p className="text-green-600">
            Avg Return: {payload[0].payload.returns}%
          </p>
        </div>
      )
    }
    return null
  }

  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{payload[0].name}</p>
          <p className="text-blue-600">
            Allocation: {formatPercent(payload[0].value)}
          </p>
          <p className="text-green-600">
            Amount: {formatCurrency(payload[0].payload.amount)}
          </p>
        </div>
      )
    }
    return null
  }

  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  if (type === 'pie') {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={mockPieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {mockPieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomPieTooltip />} />
        </PieChart>
      </ResponsiveContainer>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={mockBarData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey="name" 
          stroke="#666"
          fontSize={12}
        />
        <YAxis 
          tickFormatter={formatPercent}
          stroke="#666"
          fontSize={12}
        />
        <Tooltip content={<CustomBarTooltip />} />
        <Bar 
          dataKey="value" 
          fill={colors[0]}
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}
