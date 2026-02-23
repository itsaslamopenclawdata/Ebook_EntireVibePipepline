/**
 * Lighthouse CI Configuration
 *
 * Performance budgets and thresholds for the Vibe PDF Platform frontend.
 *
 * Run Lighthouse CI:
 * - lhci autorun --collect.url=http://localhost:3000
 * - lhci autorun --config=lighthouse-config.js
 *
 * Documentation: https://github.com/GoogleChrome/lighthouse-ci
 */

module.exports = {
  ci: {
    collect: {
      // URLs to audit
      url: [
        'http://localhost:3000',
        'http://localhost:3000/dashboard',
        'http://localhost:3000/book-creation',
      ],

      // Number of runs per URL
      numberOfRuns: 3,

      // Static dist dir (alternative to URL)
      // staticDistDir: './dist',

      // Chrome flags
      chromeFlags: '--no-sandbox --disable-dev-shm-usage',

      // Settings for collection
      settings: {
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
        emulatedFormFactor: 'desktop',
        throttling: {
          rttMs: 40,
          throughputKbps: 10 * 1024,
          cpuSlowdownMultiplier: 1,
          requestLatencyMs: 0,
          downloadThroughputKbps: 0,
          uploadThroughputKbps: 0,
        },
        screenEmulation: {
          mobile: false,
          width: 1920,
          height: 1080,
          deviceScaleFactor: 1,
          disabled: false,
        },
      },
    },

    assert: {
      // Performance budgets
      assertions: {
        // Categories (scores out of 100)
        'categories:performance': ['error', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],

        // Core Web Vitals
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }], // 1.8s
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }], // 2.5s
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }], // 300ms
        'speed-index': ['error', { maxNumericValue: 3400 }], // 3.4s

        // Budgets
        'resource-summary': {
          maxSize: 200, // KB (script)
        },
        'max-potential-fid': ['warn', { maxNumericValue: 100 }], // 100ms

        // Custom budgets by resource type
        'script-budget': ['error', { maxSize: 500 * 1024 }], // 500KB for JS
        'stylesheet-budget': ['error', { maxSize: 50 * 1024 }], // 50KB for CSS
        'total-byte-weight': ['warn', { maxSize: 1500 * 1024 }], // 1.5MB total
        'unused-javascript': ['warn', { maxLength: 100 * 1024 }], // 100KB
        'unused-css-rules': ['warn', { maxLength: 50 * 1024 }], // 50KB

        // Performance metrics
        'render-blocking-resources': ['warn', { maxLength: 0 }],
        'uses-responsive-images': ['warn', { maxLength: 0 }],
        'modern-image-formats': ['warn', { maxLength: 0 }], // Should use WebP/AVIF
        'offscreen-images': ['warn', { maxLength: 0 }],
        'unminified-css': ['warn', { maxLength: 0 }],
        'unminified-javascript': ['warn', { maxLength: 0 }],

        // Best practices
        'no-document-write': ['error', { maxLength: 0 }],
        'no-vulnerable-libraries': ['error', { maxLength: 0 }],
        'js-libraries': ['warn', { maxLength: 5 }], // Max 5 JS libraries
        'uses-http2': ['warn', { maxLength: 0 }], // Should use HTTP/2

        // Accessibility
        'color-contrast': ['error', { maxLength: 0 }],
        'label': ['error', { maxLength: 0 }],
        'link-name': ['error', { maxLength: 0 }],
        'image-alt': ['error', { maxLength: 0 }],

        // SEO
        'meta-description': ['warn', { maxLength: 0 }],
        'http-status-code': ['error', { maxLength: 0 }],
        'link-text': ['warn', { maxLength: 0 }],
        'is-crawlable': ['error', { maxLength: 0 }],
        'robots-txt': ['warn', { maxLength: 0 }],
        'canonical': ['warn', { maxLength: 0 }],
      },

      // Aggregate assertion mode
      preset: 'lighthouse:recommended',

      // Assert preset
      aggregateAssertions: {
        // Assert against median runs
        minMedianPerformance: 0.8,

        // Assert against all runs
        maxFailedRuns: 1, // Allow 1 failure out of 3 runs
      },
    },

    upload: {
      // Upload to Lighthouse CI server
      target: 'temporary-public-storage',

      // Or configure your own server
      // serverBaseUrl: 'http://localhost:9001',

      // GitHub integration
      // githubAppToken: process.env.LHCI_GITHUB_APP_TOKEN,

      // Build details
      uploadUrlMap: true,
      reportFilenamePattern: '%%PATHNAME%%-%%DATETIME%%-report.%%EXTENSION%%',
    },

    server: {
      // Server configuration for collecting LHCIs
      port: 9001,
      storage: {
        storageMethod: 'sql',
        sqlDialect: 'sqlite',
        sqlDatabasePath: './lhci.db',
      },
    },
  },
};
