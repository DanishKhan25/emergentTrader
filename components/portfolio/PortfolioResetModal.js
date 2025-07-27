'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { AlertTriangle, RefreshCw, Trash2 } from 'lucide-react'

export default function PortfolioResetModal({ isOpen, onClose, onReset }) {
  const [loading, setLoading] = useState(false)
  const [resetType, setResetType] = useState('signals') // 'signals' or 'all'

  const handleReset = async () => {
    setLoading(true)
    try {
      if (resetType === 'signals') {
        // Clear only signal positions
        const response = await fetch('http://localhost:8000/signals/clear', {
          method: 'DELETE'
        })
        const result = await response.json()
        if (result.success) {
          alert('Signal positions cleared successfully!')
        } else {
          throw new Error(result.error)
        }
      } else {
        // Reset everything (would need additional endpoint)
        alert('Full reset not implemented yet')
      }
      
      onReset()
      onClose()
    } catch (err) {
      alert(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            <span>Reset Portfolio</span>
          </DialogTitle>
          <DialogDescription>
            Choose what you want to reset in your portfolio
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="bg-yellow-50 p-4 rounded-md">
            <h4 className="font-medium text-yellow-800 mb-2">⚠️ Warning</h4>
            <p className="text-sm text-yellow-700">
              This action cannot be undone. Please choose carefully what you want to reset.
            </p>
          </div>

          <div className="space-y-3">
            <div 
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                resetType === 'signals' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setResetType('signals')}
            >
              <div className="flex items-center space-x-3">
                <input 
                  type="radio" 
                  checked={resetType === 'signals'} 
                  onChange={() => setResetType('signals')}
                  className="text-blue-600"
                />
                <div>
                  <h4 className="font-medium">Clear Signal Positions Only</h4>
                  <p className="text-sm text-gray-600">
                    Remove all auto-generated signal positions but keep manual positions and funds
                  </p>
                </div>
              </div>
            </div>

            <div 
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                resetType === 'all' ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setResetType('all')}
            >
              <div className="flex items-center space-x-3">
                <input 
                  type="radio" 
                  checked={resetType === 'all'} 
                  onChange={() => setResetType('all')}
                  className="text-red-600"
                />
                <div>
                  <h4 className="font-medium text-red-700">Reset Everything</h4>
                  <p className="text-sm text-gray-600">
                    Clear all positions and reset funds to default (₹10,00,000)
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-md">
            <h4 className="font-medium text-blue-800 mb-2">💡 Recommendation</h4>
            <p className="text-sm text-blue-700">
              For testing the manual position features, choose "Clear Signal Positions Only" 
              to keep your manual positions and start with a clean slate.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleReset}
            disabled={loading}
            variant={resetType === 'all' ? 'destructive' : 'default'}
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Resetting...
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4 mr-2" />
                {resetType === 'signals' ? 'Clear Signals' : 'Reset All'}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
