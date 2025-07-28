#!/usr/bin/env node
/**
 * Script to clear frontend cache and force refresh of Shariah stocks data
 */

const fs = require('fs');
const path = require('path');

console.log('🧹 Clearing Frontend Cache...');

// Clear Next.js cache
const nextCacheDir = path.join(__dirname, '.next');
if (fs.existsSync(nextCacheDir)) {
    try {
        fs.rmSync(nextCacheDir, { recursive: true, force: true });
        console.log('✅ Cleared Next.js cache');
    } catch (error) {
        console.log('⚠️  Could not clear Next.js cache:', error.message);
    }
}

// Clear any browser cache files
const cacheFiles = [
    '.next/cache',
    'node_modules/.cache',
    '.cache'
];

cacheFiles.forEach(cacheFile => {
    const cachePath = path.join(__dirname, cacheFile);
    if (fs.existsSync(cachePath)) {
        try {
            fs.rmSync(cachePath, { recursive: true, force: true });
            console.log(`✅ Cleared ${cacheFile}`);
        } catch (error) {
            console.log(`⚠️  Could not clear ${cacheFile}:`, error.message);
        }
    }
});

console.log('✅ Frontend cache cleared!');
console.log('🔄 Please restart your Next.js app to see the updated Shariah stocks count.');
console.log('💡 Run: npm run dev');
