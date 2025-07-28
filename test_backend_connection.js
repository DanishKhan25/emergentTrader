#!/usr/bin/env node

/**
 * Test script to verify frontend can connect to Python backend
 * Run with: node test_backend_connection.js
 */

const fetch = require('node-fetch');

const BACKEND_URL = 'http://localhost:8000';

async function testBackendConnection() {
    console.log('🔗 Testing Backend Connection...');
    console.log(`Backend URL: ${BACKEND_URL}`);
    
    const tests = [
        {
            name: 'Health Check',
            url: `${BACKEND_URL}/health`,
            method: 'GET'
        },
        {
            name: 'Signals Endpoint',
            url: `${BACKEND_URL}/signals`,
            method: 'GET',
            requiresAuth: true
        },
        {
            name: 'Active Signals',
            url: `${BACKEND_URL}/signals/active`,
            method: 'GET',
            requiresAuth: true
        },
        {
            name: 'Signal Statistics',
            url: `${BACKEND_URL}/signals/statistics`,
            method: 'GET',
            requiresAuth: true
        }
    ];
    
    for (const test of tests) {
        try {
            console.log(`\n📡 Testing ${test.name}...`);
            
            const headers = {
                'Content-Type': 'application/json'
            };
            
            // Add mock auth header if required
            if (test.requiresAuth) {
                headers['Authorization'] = 'Bearer mock_token_for_testing';
            }
            
            const response = await fetch(test.url, {
                method: test.method,
                headers: headers
            });
            
            console.log(`   Status: ${response.status} ${response.statusText}`);
            
            if (response.ok) {
                const data = await response.json();
                console.log(`   ✅ Success`);
                
                if (data.success !== undefined) {
                    console.log(`   Response Success: ${data.success}`);
                }
                
                if (data.count !== undefined) {
                    console.log(`   Count: ${data.count}`);
                }
                
                if (data.error) {
                    console.log(`   Error: ${data.error}`);
                }
            } else {
                console.log(`   ❌ Failed`);
                
                if (response.status === 401) {
                    console.log(`   Note: Authentication required (expected for protected endpoints)`);
                } else if (response.status === 404) {
                    console.log(`   Note: Endpoint not found`);
                } else {
                    const text = await response.text();
                    console.log(`   Response: ${text.substring(0, 200)}...`);
                }
            }
            
        } catch (error) {
            console.log(`   💥 Connection Error: ${error.message}`);
            
            if (error.code === 'ECONNREFUSED') {
                console.log(`   🚨 Backend server is not running on port 8000`);
                console.log(`   💡 Start the backend with: cd python_backend && python main_enhanced.py`);
            }
        }
    }
    
    console.log('\n📋 Connection Test Summary:');
    console.log('✅ If you see status 200 or 401 (auth required), the connection is working');
    console.log('❌ If you see connection errors, start the Python backend server');
    console.log('🚀 Backend should be running on: http://localhost:8000');
}

// Run the test
testBackendConnection().catch(console.error);
