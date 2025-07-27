'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { AlertCircle, DollarSign } from 'lucide-react'

export default function AddPositionModal({ isOpen, onClose, onAdd, availableFunds }) {
  const [formData, setFormData] = useState({
    symbol: '',
    quantity: '',
    entry_price: '',
    strategy: '',
    target_price: '',
    stop_loss: '',
    notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const strategies = [
    { value: 'multibagger', label: 'Multibagger' },
    { value: 'momentum', label: 'Momentum' },
    { value: 'swing', label: 'Swing Trading' },
    { value: 'value_investing', label: 'Value Investing' },
    { value: 'breakout', label: 'Breakout' },
    { value: 'mean_reversion', label: 'Mean Reversion' }
  ]

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError('')

    // Auto-calculate target and stop loss
    if (field === 'entry_price' && value) {
      const entryPrice = parseFloat(value)
      if (!isNaN(entryPrice)) {
        setFormData(prev => ({
          ...prev,
          target_price: (entryPrice * 1.2).toFixed(2), // 20% target
          stop_loss: (entryPrice * 0.9).toFixed(2) // 10% stop loss
        }))
      }
    }
  }

  const calculateInvestment = () => {
    const quantity = parseFloat(formData.quantity) || 0
    const price = parseFloat(formData.entry_price) || 0
    return quantity * price
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Validation
      const requiredFields = ['symbol', 'quantity', 'entry_price', 'strategy']
      for (const field of requiredFields) {
        if (!formData[field]) {
          throw new Error(`${field.replace('_', ' ')} is required`)
        }
      }

      const investment = calculateInvestment()
      if (investment > availableFunds) {
        throw new Error(`Insufficient funds. Available: ₹${availableFunds.toLocaleString()}`)
      }

      // Prepare data
      const positionData = {
        ...formData,
        symbol: formData.symbol.toUpperCase(),
        quantity: parseFloat(formData.quantity),
        entry_price: parseFloat(formData.entry_price),
        target_price: parseFloat(formData.target_price) || parseFloat(formData.entry_price) * 1.2,
        stop_loss: parseFloat(formData.stop_loss) || parseFloat(formData.entry_price) * 0.9
      }

      await onAdd(positionData)
      
      // Reset form
      setFormData({
        symbol: '',
        quantity: '',
        entry_price: '',
        strategy: '',
        target_price: '',
        stop_loss: '',
        notes: ''
      })
      
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const investment = calculateInvestment()

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add New Position</DialogTitle>
          <DialogDescription>
            Add a new stock position to your portfolio
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-md">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="symbol">Stock Symbol *</Label>
              <Input
                id="symbol"
                placeholder="e.g., RELIANCE"
                value={formData.symbol}
                onChange={(e) => handleInputChange('symbol', e.target.value.toUpperCase())}
                className="uppercase"
              />
            </div>
            <div>
              <Label htmlFor="strategy">Strategy *</Label>
              <Select value={formData.strategy} onValueChange={(value) => handleInputChange('strategy', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select strategy" />
                </SelectTrigger>
                <SelectContent>
                  {strategies.map((strategy) => (
                    <SelectItem key={strategy.value} value={strategy.value}>
                      {strategy.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="quantity">Quantity *</Label>
              <Input
                id="quantity"
                type="number"
                placeholder="100"
                value={formData.quantity}
                onChange={(e) => handleInputChange('quantity', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="entry_price">Entry Price *</Label>
              <Input
                id="entry_price"
                type="number"
                step="0.01"
                placeholder="2500.00"
                value={formData.entry_price}
                onChange={(e) => handleInputChange('entry_price', e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="target_price">Target Price</Label>
              <Input
                id="target_price"
                type="number"
                step="0.01"
                placeholder="Auto-calculated"
                value={formData.target_price}
                onChange={(e) => handleInputChange('target_price', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="stop_loss">Stop Loss</Label>
              <Input
                id="stop_loss"
                type="number"
                step="0.01"
                placeholder="Auto-calculated"
                value={formData.stop_loss}
                onChange={(e) => handleInputChange('stop_loss', e.target.value)}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              placeholder="Add any notes about this position..."
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              rows={2}
            />
          </div>

          {/* Investment Summary */}
          <div className="bg-blue-50 p-4 rounded-md space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Investment Required:</span>
              <span className="font-bold text-blue-600">
                ₹{investment.toLocaleString('en-IN')}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Available Funds:</span>
              <span className="text-sm">₹{availableFunds.toLocaleString('en-IN')}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Remaining After:</span>
              <span className={`text-sm font-medium ${
                (availableFunds - investment) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ₹{(availableFunds - investment).toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        </form>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            onClick={handleSubmit}
            disabled={loading || investment > availableFunds}
          >
            {loading ? 'Adding...' : 'Add Position'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
