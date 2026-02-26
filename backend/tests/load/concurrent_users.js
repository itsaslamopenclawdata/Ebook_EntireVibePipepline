/**
 * Load Test: Concurrent User Simulation
 * Simulates multiple concurrent users performing various operations.
 * 
 * Run with: node backend/tests/load/concurrent_users.js
 */

const http = require('http');
const https = require('https');

// Configuration
const CONFIG = {
  baseUrl: process.env.BASE_URL || 'http://localhost:3000',
  concurrentUsers: parseInt(process.env.CONCURRENT_USERS) || 20,
  duration: parseInt(process.env.DURATION) || 60, // seconds
  rampUpTime: parseInt(process.env.RAMP_UP) || 5, // seconds
  userScenarios: [
    { name: 'browse_library', weight: 40 },
    { name: 'view_book', weight: 25 },
    { name: 'create_book', weight: 15 },
    { name: 'generate_pdf', weight: 10 },
    { name: 'user_profile', weight: 10 },
  ],
};

// User simulation data
const users = [];
const results = {
  users: CONFIG.concurrentUsers,
  duration: 0,
  operations: {
    browse_library: { total: 0, success: 0, failed: 0, avgTime: 0 },
    view_book: { total: 0, success: 0, failed: 0, avgTime: 0 },
    create_book: { total: 0, success: 0, failed: 0, avgTime: 0 },
    generate_pdf: { total: 0, success: 0, failed: 0, avgTime: 0 },
    user_profile: { total: 0, success: 0, failed: 0, avgTime: 0 },
  },
  errors: {},
  responseTimes: [],
  startTime: null,
  endTime: null,
};

/**
 * Make HTTP request
 */
function makeRequest(path, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const url = new URL(path, CONFIG.baseUrl);
    
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: 30000,
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
          data: data.substring(0, 500),
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

    if (body) {
      req.write(JSON.stringify(body));
    }

    req.end();
  });
}

/**
 * Get random operation based on weights
 */
function getRandomOperation() {
  const totalWeight = CONFIG.userScenarios.reduce((sum, s) => sum + s.weight, 0);
  let random = Math.random() * totalWeight;
  
  for (const scenario of CONFIG.userScenarios) {
    random -= scenario.weight;
    if (random <= 0) {
      return scenario.name;
    }
  }
  
  return CONFIG.userScenarios[0].name;
}

/**
 * Execute user operation
 */
async function executeOperation(operationName) {
  const operationResults = results.operations[operationName];
  operationResults.total++;
  
  try {
    let result;
    
    switch (operationName) {
      case 'browse_library':
        result = await makeRequest('/api/v1/books/');
        break;
        
      case 'view_book':
        result = await makeRequest(`/api/v1/books/book_${Math.floor(Math.random() * 100)}`);
        break;
        
      case 'create_book':
        result = await makeRequest('/api/v1/books/', 'POST', {
          title: `Test Book ${Date.now()}`,
          description: 'Load test book',
        });
        break;
        
      case 'generate_pdf':
        result = await makeRequest('/api/v1/generation/start', 'POST', {
          book_id: 'book123',
          options: { quality: 'medium' },
        });
        break;
        
      case 'user_profile':
        result = await makeRequest('/api/v1/profile/me');
        break;
        
      default:
        result = await makeRequest('/health');
    }
    
    if (result.statusCode >= 200 && result.statusCode < 400) {
      operationResults.success++;
    } else {
      operationResults.failed++;
      const errorKey = `${operationName}_HTTP_${result.statusCode}`;
      results.errors[errorKey] = (results.errors[errorKey] || 0) + 1;
    }
    
    results.responseTimes.push(result.responseTime);
    
    return result.responseTime;
    
  } catch (error) {
    operationResults.failed++;
    const errorKey = `${operationName}_${error.message}`;
    results.errors[errorKey] = (results.errors[errorKey] || 0) + 1;
    
    return -1;
  }
}

/**
 * Simulate a single user session
 */
async function simulateUser(userId) {
  console.log(`User ${userId}: Starting session`);
  
  const endTime = results.startTime + (CONFIG.duration * 1000);
  
  while (Date.now() < endTime) {
    // Get random operation
    const operationName = getRandomOperation();
    
    // Execute operation
    const responseTime = await executeOperation(operationName);
    
    if (responseTime > 0) {
      console.log(`User ${userId}: ${operationName} - ${responseTime}ms`);
    }
    
    // Think time between operations (1-3 seconds)
    const thinkTime = 1000 + Math.random() * 2000;
    await new Promise(resolve => setTimeout(resolve, thinkTime));
  }
  
  console.log(`User ${userId}: Session ended`);
}

/**
 * Calculate statistics
 */
function calculateStats() {
  const totalOps = Object.values(results.operations).reduce((sum, op) => sum + op.total, 0);
  const totalSuccess = Object.values(results.operations).reduce((sum, op) => sum + op.success, 0);
  const totalFailed = Object.values(results.operations).reduce((sum, op) => sum + op.failed, 0);
  
  // Calculate average times per operation
  for (const [name, op] of Object.entries(results.operations)) {
    op.avgTime = totalOps > 0 ? (op.total / totalOps) * 100 : 0;
    op.successRate = op.total > 0 ? (op.success / op.total) * 100 : 0;
  }
  
  // Overall stats
  const sortedTimes = results.responseTimes.sort((a, b) => a - b);
  const avgTime = sortedTimes.reduce((a, b) => a + b, 0) / sortedTimes.length;
  
  return {
    totalOperations: totalOps,
    successfulOperations: totalSuccess,
    failedOperations: totalFailed,
    successRate: totalOps > 0 ? (totalSuccess / totalOps) * 100 : 0,
    avgResponseTime: avgTime,
    p50: sortedTimes[Math.floor(sortedTimes.length * 0.5)] || 0,
    p90: sortedTimes[Math.floor(sortedTimes.length * 0.9)] || 0,
    p95: sortedTimes[Math.floor(sortedTimes.length * 0.95)] || 0,
  };
}

/**
 * Run concurrent user simulation
 */
async function runSimulation() {
  console.log('=== Concurrent User Simulation ===');
  console.log(`Base URL: ${CONFIG.baseUrl}`);
  console.log(`Concurrent Users: ${CONFIG.concurrentUsers}`);
  console.log(`Duration: ${CONFIG.duration}s`);
  console.log(`Ramp-up Time: ${CONFIG.rampUpTime}s`);
  console.log('Starting simulation...\n');
  
  results.startTime = Date.now();
  
  // Start ramp-up period
  const userPromises = [];
  
  for (let i = 0; i < CONFIG.concurrentUsers; i++) {
    // Stagger user start times during ramp-up
    const delay = (i / CONFIG.concurrentUsers) * CONFIG.rampUpTime * 1000;
    
    const userPromise = new Promise((resolve) => {
      setTimeout(async () => {
        await simulateUser(i);
        resolve();
      }, delay);
    });
    
    userPromises.push(userPromise);
  }
  
  // Wait for all users to complete
  await Promise.all(userPromises);
  
  results.endTime = Date.now();
  results.duration = (results.endTime - results.startTime) / 1000;
  
  // Calculate and display results
  const stats = calculateStats();
  
  console.log('\n=== Simulation Results ===');
  console.log(`Duration: ${results.duration.toFixed(2)}s`);
  console.log(`Total Operations: ${stats.totalOperations}`);
  console.log(`Successful: ${stats.successfulOperations}`);
  console.log(`Failed: ${stats.failedOperations}`);
  console.log(`Success Rate: ${stats.successRate.toFixed(2)}%`);
  console.log(`Operations/sec: ${(stats.totalOperations / results.duration).toFixed(2)}`);
  
  console.log('\n=== Operation Breakdown ===');
  for (const [name, op] of Object.entries(results.operations)) {
    console.log(`${name}:`);
    console.log(`  Total: ${op.total}, Success: ${op.success}, Failed: ${op.failed}`);
    console.log(`  Success Rate: ${op.successRate.toFixed(2)}%`);
  }
  
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
      duration: results.duration,
      ...stats,
      opsPerSecond: stats.totalOperations / results.duration,
    },
    operations: results.operations,
    errors: results.errors,
  };
  
  const fs = require('fs');
  const resultsDir = 'backend/tests/load/results';
  
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }
  
  fs.writeFileSync(
    `${resultsDir}/concurrent_users_results.json`,
    JSON.stringify(testResults, null, 2)
  );
  
  console.log(`\nResults saved to: ${resultsDir}/concurrent_users_results.json`);
  
  return testResults;
}

// Export for use as module
module.exports = { runSimulation, CONFIG };

// Run if executed directly
if (require.main === module) {
  runSimulation().catch(console.error);
}
