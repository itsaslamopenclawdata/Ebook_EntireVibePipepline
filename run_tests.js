#!/usr/bin/env node

/**
 * Test Runner - Runs all tests for Ebook Vibe Platform
 * Usage: node run_tests.js [options]
 * 
 * Options:
 *   --type=unit        Run unit tests only
 *   --type=integration Run integration tests only
 *   --type=e2e         Run E2E tests only
 *   --type=load        Run load tests only
 *   --type=all         Run all tests (default)
 *   --coverage         Generate coverage report
 *   --verbose          Verbose output
 * 
 * Examples:
 *   node run_tests.js                    # Run all tests
 *   node run_tests.js --type=unit        # Run unit tests only
 *   node run_tests.js --type=integration --coverage
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Parse arguments
const args = process.argv.slice(2);
const options = {
  type: 'all',
  coverage: false,
  verbose: false,
};

for (const arg of args) {
  if (arg.startsWith('--type=')) {
    options.type = arg.replace('--type=', '');
  } else if (arg === '--coverage') {
    options.coverage = true;
  } else if (arg === '--verbose') {
    options.verbose = true;
  }
}

console.log('=== Ebook Vibe Platform Test Runner ===\n');
console.log('Options:', options);

// Colors for output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function runCommand(command, cwd = process.cwd()) {
  try {
    if (options.verbose) {
      log(`Running: ${command}`, 'cyan');
    }
    execSync(command, { 
      cwd, 
      stdio: options.verbose ? 'inherit' : 'pipe',
      env: { ...process.env, FORCE_COLOR: 'true' }
    });
    return true;
  } catch (error) {
    log(`Command failed: ${command}`, 'red');
    if (options.verbose && error.stdout) {
      console.log(error.stdout.toString());
    }
    return false;
  }
}

// Run tests based on type
async function runTests() {
  const results = {
    unit: { passed: false, duration: 0 },
    integration: { passed: false, duration: 0 },
    e2e: { passed: false, duration: 0 },
    load: { passed: false, duration: 0 },
  };

  const startTime = Date.now();

  // Run backend unit tests
  if (options.type === 'all' || options.type === 'unit') {
    log('\n--- Running Unit Tests ---', 'blue');
    const unitResult = runCommand(
      `python -m pytest backend/tests/unit -v ${options.coverage ? '--cov=backend/app --cov-report=term-missing' : ''}`
    );
    results.unit.passed = unitResult;
  }

  // Run backend integration tests
  if (options.type === 'all' || options.type === 'integration') {
    log('\n--- Running Integration Tests ---', 'blue');
    const intResult = runCommand(
      `python -m pytest backend/tests/integration -v ${options.coverage ? '--cov=backend/app --cov-report=term-missing' : ''}`
    );
    results.integration.passed = intResult;
  }

  // Run E2E tests (requires Playwright)
  if (options.type === 'all' || options.type === 'e2e') {
    log('\n--- Running E2E Tests ---', 'blue');
    if (fs.existsSync('frontend/tests/e2e')) {
      const e2eResult = runCommand('npx playwright test frontend/tests/e2e');
      results.e2e.passed = e2eResult;
    } else {
      log('E2E tests not found, skipping...', 'yellow');
    }
  }

  // Run load tests
  if (options.type === 'all' || options.type === 'load') {
    log('\n--- Running Load Tests ---', 'blue');
    if (fs.existsSync('backend/tests/load')) {
      log('Running API response times test...', 'cyan');
      const loadResult1 = runCommand('node backend/tests/load/api_response_times.js');
      
      log('Running concurrent users test...', 'cyan');
      const loadResult2 = runCommand('node backend/tests/load/concurrent_users.js');
      
      results.load.passed = loadResult1 && loadResult2;
    } else {
      log('Load tests not found, skipping...', 'yellow');
    }
  }

  const endTime = Date.now();
  const totalDuration = (endTime - startTime) / 1000;

  // Print summary
  log('\n=== Test Summary ===', 'green');
  
  for (const [type, result] of Object.entries(results)) {
    if (result.passed !== undefined) {
      const status = result.passed ? 'PASSED' : 'FAILED';
      const color = result.passed ? 'green' : 'red';
      log(`  ${type}: ${status}`, color);
    }
  }

  log(`\nTotal Duration: ${totalDuration.toFixed(2)}s`, 'cyan');

  // Generate coverage report if requested
  if (options.coverage && (options.type === 'all' || options.type === 'unit' || options.type === 'integration')) {
    log('\n--- Generating Coverage Report ---', 'blue');
    runCommand('python -m pytest --cov-report=html --cov-report=term-missing');
  }

  // Exit with error code if any tests failed
  const allPassed = Object.values(results).every(r => r.passed !== false);
  if (!allPassed) {
    log('\nSome tests failed!', 'red');
    process.exit(1);
  }

  log('\nAll tests passed!', 'green');
}

// Run tests
runTests().catch(error => {
  log(`Error running tests: ${error.message}`, 'red');
  process.exit(1);
});
