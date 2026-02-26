/**
 * Load Test: API Response Times
 * Tests API endpoint response times under various load conditions.
 * 
 * Run with: npx loadtest -c 10 -n 1000 http://localhost:3000/api/health
 * Or use: node backend/tests/load/api_response_times.js
 */

const http = require('http');
const https = require('https');

// Configuration
const CONFIG = {
  baseUrl: process.env.BASE_URL || 'http://localhost:3000',
  endpoints: [
    { path: '/api/v1/auth/login', method: 'POST', weight: 3 },
    { path: '/api/v1/books/', method: 'GET', weight: 2 },
    { path: '/api/v1/books/book123', method: 'GET', weight: 2 },
    { path: '/api/v1/profile/me', method: 'GET', weight: 1 },
    { path: '/health', method: 'GET', weight: 1 },
  ],
  concurrentUsers: parseInt(process.env.CONCURRENT_USERS) || 10,
  requestsPerUser: parseInt(process.env.REQUESTS_PER_USER) || 50,
  timeout: parseInt(process.env.TIMEOUT) || 30000,
};

// Results storage
const results = {
  totalRequests: 0,
  successfulRequests: 0,
  failedRequests: 0,
  responseTimes: [],
  errors: {},
};

/**
 * Make HTTP request
 */
function makeRequest(endpoint) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const url = new URL(endpoint.path, CONFIG.baseUrl);
    
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: endpoint.method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: CONFIG.timeout,
    };

    const protocol = url.protocol === 'https:' ? https : http;
    
    const req = protocol.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        resolve({
          statusCode: res.statusCode,
          responseTime,
          data: data.substring(0, 1000), // First 1000 chars
        });
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    // Add request body for POST
    if (endpoint.method === 'POST') {
      req.write(JSON.stringify({
        username: 'testuser',
        password: 'testpass',
      }));
    }

    req.end();
  });
}

/**
 * Simulate user behavior
 */
async function simulateUser(userId) {
  const endpoint = CONFIG.endpoints[Math.floor(Math.random() * CONFIG.endpoints.length)];
  
  try {
    const result = await makeRequest(endpoint);
    
    results.totalRequests++;
    
    if (result.statusCode >= 200 && result.statusCode < 400) {
      results.successfulRequests++;
    } else {
      results.failedRequests++;
      const errorKey = `HTTP_${result.statusCode}`;
      results.errors[errorKey] = (results.errors[errorKey] || 0) + 1;
    }
    
    results.responseTimes.push(result.responseTime);
    
    console.log(`User ${userId}: ${endpoint.method} ${endpoint.path} - ${result.statusCode} (${result.responseTime}ms)`);
    
  } catch (error) {
    results.totalRequests++;
    results.failedRequests++;
    const errorKey = error.message || 'UNKNOWN';
    results.errors[errorKey] = (results.errors[errorKey] || 0) + 1;
    
    console.error(`User ${userId}: Error - ${error.message}`);
  }
}

/**
 * Run load test
 */
async function runLoadTest() {
  console.log('=== API Response Times Load Test ===');
  console.log(`Base URL: ${CONFIG.baseUrl}`);
  console.log(`Concurrent Users: ${CONFIG.concurrentUsers}`);
  console.log(`Requests per User: ${CONFIG.requestsPerUser}`);
  console.log('Starting test...\n');

  const startTime = Date.now();
  const promises = [];

  // Create concurrent users
  for (let i = 0; i < CONFIG.concurrentUsers; i++) {
    const userPromise = (async () => {
      for (let j = 0; j < CONFIG.requestsPerUser; j++) {
        await simulateUser(i);
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
      }
    })();
    
    promises.push(userPromise);
  }

  await Promise.all(promises);
  
  const endTime = Date.now();
  const totalDuration = endTime - startTime;

  // Calculate statistics
  const sortedTimes = results.responseTimes.sort((a, b) => a - b);
  const avgResponseTime = results.responseTimes.reduce((a, b) => a + b, 0) / results.responseTimes.length;
  const p50 = sortedTimes[Math.floor(sortedTimes.length * 0.5)] || 0;
  const p90 = sortedTimes[Math.floor(sortedTimes.length * 0.9)] || 0;
  const p95 = sortedTimes[Math.floor(sortedTimes.length * 0.95)] || 0;
  const p99 = sortedTimes[Math.floor(sortedTimes.length * 0.99)] || 0;
  const minResponseTime = sortedTimes[0] || 0;
  const maxResponseTime = sortedTimes[sortedTimes.length - 1] || 0;
  const rps = (results.totalRequests / totalDuration) * 1000;

  // Print results
  console.log('\n=== Test Results ===');
  console.log(`Total Duration: ${(totalDuration / 1000).toFixed(2)}s`);
  console.log(`Total Requests: ${results.totalRequests}`);
  console.log(`Successful: ${results.successfulRequests}`);
  console.log(`Failed: ${results.failedRequests}`);
  console.log(`Success Rate: ${((results.successfulRequests / results.totalRequests) * 100).toFixed(2)}%`);
  console.log(`Requests/sec: ${rps.toFixed(2)}`);
  console.log('\n=== Response Times (ms) ===');
  console.log(`Min: ${minResponseTime}`);
  console.log(`Avg: ${avgResponseTime.toFixed(2)}`);
  console.log(`P50: ${p50}`);
  console.log(`P90: ${p90}`);
  console.log(`P95: ${p95}`);
  console.log(`P99: ${p99}`);
  console.log(`Max: ${maxResponseTime}`);

  if (Object.keys(results.errors).length > 0) {
    console.log('\n=== Errors ===');
    for (const [error, count] of Object.entries(results.errors)) {
      console.log(`${error}: ${count}`);
    }
  }

  // Export results
  const testResults = {
    timestamp: new Date().toISOString(),
    config: CONFIG,
    summary: {
      totalDuration,
      totalRequests: results.totalRequests,
      successfulRequests: results.successfulRequests,
      failedRequests: results.failedRequests,
      successRate: (results.successfulRequests / results.totalRequests) * 100,
      rps,
    },
    responseTimes: {
      min: minResponseTime,
      avg: avgResponseTime,
      p50,
      p90,
      p95,
      p99,
      max: maxResponseTime,
    },
    errors: results.errors,
  };

  // Save to file
  const fs = require('fs');
  fs.writeFileSync(
    'backend/tests/load/results/api_response_times_results.json',
    JSON.stringify(testResults, null, 2)
  );

  console.log('\nResults saved to: backend/tests/load/results/api_response_times_results.json');

  return testResults;
}

// Export for use as module
module.exports = { runLoadTest, CONFIG };

// Run if executed directly
if (require.main === module) {
  runLoadTest().catch(console.error);
}
