// Simple test to check if portfolio page loads correctly
const { execSync } = require('child_process');

console.log('Testing portfolio page...');

try {
  // Test if the page loads without errors
  const result = execSync('curl -s -w "%{http_code}" http://localhost:3000/portfolio -o /dev/null', { encoding: 'utf8' });
  
  if (result.trim() === '200') {
    console.log('✅ Portfolio page loads successfully (HTTP 200)');
  } else {
    console.log(`❌ Portfolio page failed to load (HTTP ${result.trim()})`);
    process.exit(1);
  }

  // Test if the page contains expected content
  const content = execSync('curl -s http://localhost:3000/portfolio', { encoding: 'utf8' });
  
  const checks = [
    { name: 'Portfolio title', test: content.includes('Portfolio') },
    { name: 'MainLayout component', test: content.includes('EmergentTrader') },
    { name: 'Navigation menu', test: content.includes('Dashboard') && content.includes('Stocks') },
    { name: 'Portfolio cards structure', test: content.includes('Total Value') },
    { name: 'React hydration', test: content.includes('__next_f') }
  ];

  checks.forEach(check => {
    if (check.test) {
      console.log(`✅ ${check.name} - Found`);
    } else {
      console.log(`❌ ${check.name} - Missing`);
    }
  });

  // Check if it's showing loading state or actual data
  if (content.includes('animate-pulse')) {
    console.log('⚠️  Page is showing loading state');
  } else if (content.includes('₹') && !content.includes('₹0')) {
    console.log('✅ Page is showing portfolio data');
  } else {
    console.log('⚠️  Page might be showing empty/default data');
  }

  console.log('\nPortfolio page test completed!');

} catch (error) {
  console.error('❌ Error testing portfolio page:', error.message);
  process.exit(1);
}
