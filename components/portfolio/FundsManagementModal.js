'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertCircle, Plus, Minus, DollarSign } from 'lucide-react'

export default function FundsManagementModal({ isOpen, onClose, onUpdate, funds }) {
  const [activeTab, setActiveTab] = useState('add')
  const [amount, setAmount] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (action) => {
    setLoading(true)
    setError('')

    try {
      const value = parseFloat(amount)
      if (!value || value <= 0) {
        throw new Error('Please enter a valid amount')
      }

      if (action === 'withdraw' && value > funds.available_funds) {
        throw new Error(`Insufficient available funds. Available: ₹${funds.available_funds.toLocaleString()}`)
      }

      const updateData = {}
      if (action === 'add') {
        updateData.add_funds = value
      } else if (action === 'withdraw') {
        updateData.withdraw_funds = value
      } else if (action === 'set') {
        updateData.total_funds = value
      }

      await onUpdate(updateData)
      setAmount('')
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Manage Portfolio Funds</DialogTitle>
          <DialogDescription>
            Add funds, withdraw money, or update your total portfolio balance
          </DialogDescription>
        </DialogHeader>

        {/* Current Funds Summary */}
        <div className="bg-gray-50 p-4 rounded-md space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Total Funds:</span>
            <span className="font-bold">₹{funds.total_funds.toLocaleString('en-IN')}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Available:</span>
            <span className="text-green-600 font-medium">₹{funds.available_funds.toLocaleString('en-IN')}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Invested:</span>
            <span className="text-blue-600 font-medium">₹{funds.invested_funds.toLocaleString('en-IN')}</span>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="add">Add Funds</TabsTrigger>
            <TabsTrigger value="withdraw">Withdraw</TabsTrigger>
            <TabsTrigger value="set">Set Total</TabsTrigger>
          </TabsList>

          <div className="mt-4">
            {error && (
              <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-md mb-4">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <TabsContent value="add" className="space-y-4">
              <div>
                <Label htmlFor="add-amount">Amount to Add</Label>
                <Input
                  id="add-amount"
                  type="number"
                  placeholder="50000"
                  value={amount}
                  onChange={(e) => {
                    setAmount(e.target.value)
                    setError('')
                  }}
                />
                <p className="text-sm text-gray-500 mt-1">
                  This will increase your total and available funds
                </p>
              </div>
              <div className="bg-green-50 p-3 rounded-md">
                <div className="flex items-center space-x-2 text-green-700">
                  <Plus className="h-4 w-4" />
                  <span className="text-sm font-medium">After adding ₹{amount || '0'}:</span>
                </div>
                <div className="mt-2 space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Total Funds:</span>
                    <span>₹{(funds.total_funds + (parseFloat(amount) || 0)).toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Available:</span>
                    <span>₹{(funds.available_funds + (parseFloat(amount) || 0)).toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="withdraw" className="space-y-4">
              <div>
                <Label htmlFor="withdraw-amount">Amount to Withdraw</Label>
                <Input
                  id="withdraw-amount"
                  type="number"
                  placeholder="25000"
                  value={amount}
                  onChange={(e) => {
                    setAmount(e.target.value)
                    setError('')
                  }}
                  max={funds.available_funds}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Maximum: ₹{funds.available_funds.toLocaleString('en-IN')} (available funds)
                </p>
              </div>
              <div className="bg-red-50 p-3 rounded-md">
                <div className="flex items-center space-x-2 text-red-700">
                  <Minus className="h-4 w-4" />
                  <span className="text-sm font-medium">After withdrawing ₹{amount || '0'}:</span>
                </div>
                <div className="mt-2 space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Total Funds:</span>
                    <span>₹{(funds.total_funds - (parseFloat(amount) || 0)).toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Available:</span>
                    <span>₹{(funds.available_funds - (parseFloat(amount) || 0)).toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="set" className="space-y-4">
              <div>
                <Label htmlFor="set-amount">New Total Amount</Label>
                <Input
                  id="set-amount"
                  type="number"
                  placeholder="1000000"
                  value={amount}
                  onChange={(e) => {
                    setAmount(e.target.value)
                    setError('')
                  }}
                />
                <p className="text-sm text-gray-500 mt-1">
                  This will set your total portfolio funds to this amount
                </p>
              </div>
              <div className="bg-blue-50 p-3 rounded-md">
                <div className="flex items-center space-x-2 text-blue-700">
                  <DollarSign className="h-4 w-4" />
                  <span className="text-sm font-medium">After setting to ₹{amount || '0'}:</span>
                </div>
                <div className="mt-2 space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Total Funds:</span>
                    <span>₹{(parseFloat(amount) || 0).toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Available:</span>
                    <span>₹{((parseFloat(amount) || 0) - funds.invested_funds).toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>
            </TabsContent>
          </div>
        </Tabs>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={() => handleSubmit(activeTab)}
            disabled={loading || !amount || parseFloat(amount) <= 0}
          >
            {loading ? 'Updating...' : 
             activeTab === 'add' ? 'Add Funds' :
             activeTab === 'withdraw' ? 'Withdraw' : 'Update Total'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
