// Debug script to test portfolio page functionality
console.log('Testing portfolio page mock data...');

const mockPortfolio = {
  totalValue: 2456789,
  totalInvested: 1850000,
  totalPnL: 606789,
  totalPnLPercent: 32.8,
  dayPnL: 23456,
  dayPnLPercent: 0.96,
  activePositions: 12,
  completedTrades: 45,
  winRate: 78.3,
  bestPerformer: { symbol: 'CLEAN', return: 287.5 },
  worstPerformer: { symbol: 'IDEA', return: -12.3 },
  allocation: [
    { strategy: 'Multibagger', value: 1234567, percentage: 50.3, color: '#3B82F6' },
    { strategy: 'Momentum', value: 654321, percentage: 26.6, color: '#10B981' },
    { strategy: 'Swing', value: 345678, percentage: 14.1, color: '#F59E0B' },
    { strategy: 'Breakout', value: 222223, percentage: 9.0, color: '#EF4444' }
  ],
  riskMetrics: {
    sharpeRatio: 2.34,
    maxDrawdown: 15.2,
    volatility: 24.8,
    beta: 1.12
  }
};

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value);
};

console.log('Mock Portfolio Data:');
console.log('Total Value:', formatCurrency(mockPortfolio.totalValue));
console.log('Total P&L:', formatCurrency(mockPortfolio.totalPnL));
console.log('Active Positions:', mockPortfolio.activePositions);
console.log('Win Rate:', mockPortfolio.winRate + '%');

console.log('\nTesting formatCurrency function:');
console.log('2456789 formatted:', formatCurrency(2456789));
console.log('606789 formatted:', formatCurrency(606789));

console.log('\nMock data structure looks correct!');
