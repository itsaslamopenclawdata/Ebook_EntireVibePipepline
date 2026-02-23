# Performance Baseline Metrics

**Project:** Vibe PDF Book Generation Platform
**Last Updated:** 2026-02-21
**Environment:** Development (Local)
**Browser:** Chromium (via Playwright)

---

## Overview

This document establishes performance baseline metrics for the Vibe PDF Platform frontend. These baselines serve as:
1. **Performance budgets** for CI/CD pipelines
2. **Regression detection** thresholds
3. **Optimization targets** for development

## Test Execution

### Run Performance Tests
```bash
cd F:\Ebook\vibe-pdf-platform\Frontend

# Run all performance tests
npm run test:performance

# Run specific test suites
npx playwright test tests/performance/core-web-vitals.spec.ts
npx playwright test tests/performance/bundle-size.spec.ts
npx playwright test tests/performance/render-performance.spec.ts
npx playwright test tests/performance/api-performance.spec.ts
npx playwright test tests/performance/navigation-performance.spec.ts
```

### Run Lighthouse CI
```bash
cd F:\Ebook\vibe-pdf-platform\Frontend

# Run full Lighthouse CI audit
npm run test:lighthouse

# Collect metrics only
npm run test:lighthouse:collect

# Assert against budgets
npm run test:lighthouse:assert

# Start Lighthouse CI server
npm run test:lighthouse:server
```

---

## Core Web Vitals Baselines

### Metrics
- **LCP (Largest Contentful Paint):** < 2.5s (Good)
- **FID (First Input Delay):** < 100ms (Good)
- **CLS (Cumulative Layout Shift):** < 0.1 (Good)

### Page-Specific Targets

| Page | LCP Target | FID Target | CLS Target | Status |
|------|-----------|-----------|-----------|--------|
| Homepage (/) | 2.5s | 100ms | 0.1 | Test Ready |
| Dashboard (/dashboard) | 2.5s | 100ms | 0.1 | Test Ready |
| Book Creation (/book-creation) | 2.5s | 100ms | 0.1 | Test Ready |
| Login (/login) | 2.0s | 100ms | 0.05 | Test Ready |

### Additional Timing Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| TTFB (Time to First Byte) | < 800ms | Server response time |
| Full Page Load | < 3s | Complete page load time |
| First Contentful Paint | < 1.5s | First content rendered |
| Speed Index | < 3.4s | Visual completeness |
| Total Blocking Time | < 300ms | Main thread blocking |

---

## Bundle Size Budgets

### Initial Load Budgets

| Resource Type | Budget | Current | Status |
|--------------|--------|---------|--------|
| Initial JS Bundle | 500 KB | TBD | To Measure |
| Initial CSS Bundle | 50 KB | TBD | To Measure |
| Total Initial Transfer | 600 KB | TBD | To Measure |
| Vendor Bundle | 300 KB | TBD | To Measure |
| Individual Chunks | 200 KB | TBD | To Measure |
| Total Byte Weight | 1.5 MB | TBD | To Measure |

### Code Splitting Strategy

```
Initial Load (Route-based splitting):
├── main.<hash>.js          (Main application entry)
├── vendor.<hash>.js        (React, React Router, Zustand)
├── nextui.<hash>.js        (NextUI components, lazy loaded)
├── ui-vendor.<hash>.js     (Radix UI components, lazy loaded)
├── dashboard.<hash>.js     (Dashboard route - lazy loaded)
├── book-creation.<hash>.js (Book Creation route - lazy loaded)
└── auth.<hash>.js          (Authentication routes - lazy loaded)
```

### Compression Targets

| Metric | Target | Status |
|--------|--------|--------|
| Gzip Compression Ratio | > 70% | To Measure |
| Brotli Compression Ratio | > 75% | To Measure |
| Minification Ratio | > 40% | To Measure |

---

## Render Performance Targets

### Component Rendering

| Component Type | Target | Status |
|---------------|--------|--------|
| Initial Page Render | < 1s | Test Ready |
| Component Mount | < 100ms | Test Ready |
| List Render (100 items) | < 500ms | Test Ready |
| State Update Re-render | < 50ms | Test Ready |
| Page Transition | < 300ms | Test Ready |

### Animation & Frame Rates

| Metric | Target | Status |
|--------|--------|--------|
| Target Frame Rate | 60 FPS | Test Ready |
| Frame Time | < 16.67ms | Test Ready |
| Dropped Frames (per scroll) | < 10 | Test Ready |
| Long Tasks (> 200ms) | 0 | Test Ready |

### Virtual Scrolling

| Metric | Target | Status |
|--------|--------|--------|
| Scroll Response Time | < 100ms | Test Ready |
| DOM Nodes (vs Total Items) | < 20% | Test Ready |
| Memory Growth (per scroll) | < 5 MB | Test Ready |

---

## API Performance Targets

### Response Time Targets

| API Endpoint | P50 Target | P95 Target | P99 Target | Status |
|-------------|-----------|-----------|-----------|--------|
| GET /api/v1/books | 200ms | 500ms | 1000ms | Test Ready |
| GET /api/v1/books/{id} | 150ms | 300ms | 500ms | Test Ready |
| POST /api/v1/auth/login | 300ms | 500ms | 800ms | Test Ready |
| POST /api/v1/auth/refresh | 100ms | 200ms | 400ms | Test Ready |
| POST /api/v1/generation/start | 500ms | 1000ms | 2000ms | Test Ready |
| GET /api/v1/generation/progress/{id} | 100ms | 200ms | 400ms | Test Ready |

### WebSocket Performance

| Metric | Target | Status |
|--------|--------|--------|
| Connection Time | < 500ms | Test Ready |
| Message Latency | < 200ms | Test Ready |
| Reconnection Time | < 1s | Test Ready |

### Network Efficiency

| Metric | Target | Status |
|--------|--------|--------|
| Compression Rate | > 80% | Test Ready |
| Error Rate | < 5% | Test Ready |
| Retry Rate | < 2% | Test Ready |
| API Response Size (avg) | < 100 KB | Test Ready |

---

## Navigation Performance Targets

### Page Load Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Page Load Time | < 3s | Test Ready |
| First Contentful Paint | < 1.8s | Test Ready |
| Time to Interactive | < 3.8s | Test Ready |
| DOM Content Loaded | < 1.5s | Test Ready |

### Route Transitions

| Route | Target | Status |
|-------|--------|--------|
| Homepage -> Dashboard | < 300ms | Test Ready |
| Homepage -> Book Creation | < 300ms | Test Ready |
| Any -> Any (avg) | < 300ms | Test Ready |

### Back/Forward Navigation

| Metric | Target | Status |
|--------|--------|--------|
| Back Navigation (bfcache) | < 100ms | Test Ready |
| Forward Navigation | < 100ms | Test Ready |
| Scroll Position Restoration | Preserved | Test Ready |

---

## Lighthouse CI Configuration

### Budget Assertions

The Lighthouse CI configuration (`lighthtrc.json`) enforces the following budgets:

#### Category Scores (out of 100)
- **Performance:** >= 80 (error threshold)
- **Accessibility:** >= 90 (error threshold)
- **Best Practices:** >= 90 (error threshold)
- **SEO:** >= 90 (error threshold)

#### Core Web Vitals
- **First Contentful Paint:** <= 1.8s
- **Largest Contentful Paint:** <= 2.5s
- **Cumulative Layout Shift:** <= 0.1
- **Total Blocking Time:** <= 300ms
- **Speed Index:** <= 3.4s
- **Max Potential FID:** <= 100ms (warn)

#### Resource Budgets
- **Total Byte Weight:** <= 1.5 MB (warn)
- **Unused JavaScript:** <= 100 KB (warn)
- **Unused CSS Rules:** <= 50 KB (warn)
- **Render Blocking Resources:** 0 (warn)

### Audited URLs

- `http://localhost:3000` - Homepage
- `http://localhost:3000/dashboard` - Dashboard
- `http://localhost:3000/book-creation` - Book Creation
- `http://localhost:3000/login` - Login

---

## Performance Test Coverage

### Test Files Created

| Test File | Tests Count | Coverage |
|-----------|-------------|----------|
| `core-web-vitals.spec.ts` | 8 tests | LCP, FID, CLS across all pages |
| `bundle-size.spec.ts` | 11 tests | Bundle sizes, code splitting, compression |
| `render-performance.spec.ts` | 14 tests | Component rendering, animations, scrolling |
| `api-performance.spec.ts` | 16 tests | API response times, WebSocket, network efficiency |
| `navigation-performance.spec.ts` | 17 tests | Page load times, route transitions, navigation timing |

**Total Performance Tests:** 66 tests

### Test Categories

1. **Core Web Vitals (8 tests)**
   - Homepage LCP/FID/CLS
   - Dashboard LCP/CLS
   - Book Creation LCP/CLS
   - Combined metrics test
   - All CWV across pages

2. **Bundle Size (11 tests)**
   - Initial JS bundle size
   - Initial CSS bundle size
   - Total initial transfer size
   - Individual chunk sizes
   - Vendor bundle size
   - Route-specific bundle sizes
   - Code splitting verification
   - Baseline comparison

3. **Render Performance (14 tests)**
   - Initial page render
   - Component mount performance
   - No blocking long tasks
   - Book grid rendering (100 items)
   - Scroll performance (60fps)
   - Form input updates
   - Stepper transitions
   - Main thread blocking
   - Memoization effectiveness
   - Virtual scrolling
   - GPU acceleration
   - Animation frame rates

4. **API Performance (16 tests)**
   - Books API response times
   - Book detail API
   - Pagination performance
   - Authentication API (login, refresh)
   - Generation API (start, progress)
   - WebSocket connection & latency
   - Error handling & retries
   - Rate limiting
   - Compression verification
   - Response size validation
   - Baseline metrics collection

5. **Navigation Performance (17 tests)**
   - Initial page load times
   - First Contentful Paint (FCP)
   - Time to Interactive (TTI)
   - DOM Content Loaded timing
   - No unnecessary redirects
   - Route transition performance
   - Client-side routing verification
   - Back/forward navigation (bfcache)
   - Forward navigation
   - Scroll position restoration
   - Navigation Timing API breakdown
   - Resource loading efficiency
   - Critical rendering path
   - Above-the-fold content loading
   - Memory usage during navigation
   - Baseline metrics collection

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Performance Tests

on:
  pull_request:
    paths:
      - 'Frontend/src/**'
      - 'Frontend/tests/performance/**'
  schedule:
    - cron: '0 0 * * *' # Daily at midnight

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd Frontend
          npm ci

      - name: Build application
        run: |
          cd Frontend
          npm run build

      - name: Run performance tests
        run: |
          cd Frontend
          npm run test:performance

      - name: Run Lighthouse CI
        run: |
          cd Frontend
          npm run test:lighthouse

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: |
            Frontend/playwright-report/
            Frontend/.lighthouseci/
```

### Performance Regression Detection

If tests fail, CI/CD pipeline should:
1. **Fail the build** if metrics exceed thresholds by > 10%
2. **Warn** if metrics exceed thresholds by < 10%
3. **Create GitHub issue** for performance regression investigation
4. **Comment on PR** with performance comparison

---

## Performance Monitoring Strategy

### Local Development
- Run performance tests before committing: `npm run test:performance`
- Use Playwright UI mode: `npx playwright test --ui`
- Monitor bundle size: `npm run build:analyze`
- Run Lighthouse CI: `npm run test:lighthouse`

### Staging/Production
- Set up Lighthouse CI for critical pages
- Monitor Core Web Vitals via Google CrUX
- Track API performance with APM tools (DataDog, New Relic)
- Set up alerts for performance degradation

### Continuous Improvement
1. **Weekly:** Review performance metrics
2. **Monthly:** Update baselines based on 95th percentile
3. **Quarterly:** Performance optimization sprint
4. **Annually:** Re-evaluate performance budgets

---

## Performance Optimization Checklist

### Priority 1 (Critical - Do Now)
- [ ] Enable Gzip/Brotli compression on server
- [ ] Implement code splitting for all routes
- [ ] Lazy load images and components
- [ ] Minimize initial JavaScript bundle
- [ ] Optimize critical CSS delivery

### Priority 2 (High - Do Soon)
- [ ] Implement virtual scrolling for book grids
- [ ] Add service worker for caching
- [ ] Optimize API response sizes
- [ ] Implement request debouncing
- [ ] Add skeleton loading states

### Priority 3 (Medium - Do Later)
- [ ] Preload critical resources
- [ ] Implement HTTP/2 push for critical assets
- [ ] Optimize image formats (WebP, AVIF)
- [ ] Add resource hints (prefetch, preconnect)
- [ ] Implement edge caching with CDN

---

## Baseline Update Process

### When to Update Baselines

1. **After major feature releases** (if performance improves)
2. **After optimization sprints** (confirm improvements)
3. **Quarterly** (adjust based on user data)
4. **When environment changes** (new browser, device, etc.)

### How to Update Baselines

1. Run performance tests in production-like environment
2. Collect metrics from 10+ test runs
3. Calculate 95th percentile for each metric
4. Update thresholds in test files
5. Update this document with new baselines
6. Commit changes with `perf: update baseline metrics` message

### Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-19 | Initial baseline creation | Claude Code |
| 1.1.0 | 2026-02-21 | Added Lighthouse CI integration, navigation tests | Claude Code |

---

## Performance Tools & Resources

### Development Tools
- **Playwright:** Performance test execution
- **Lighthouse CI:** Automated performance audits
- **Vite Bundle Visualizer:** `npm run build:analyze`
- **React DevTools Profiler:** Component render analysis

### Monitoring Tools
- **Google PageSpeed Insights:** Core Web Vitals
- **WebPageTest:** Detailed performance analysis
- **Chrome DevTools Performance:** Runtime profiling
- **APM Tools:** DataDog, New Relic (for production)

### Documentation
- [Web.dev Performance Metrics](https://web.dev/metrics/)
- [Playwright Performance Testing](https://playwright.dev/docs/test-performance)
- [Vite Performance Guide](https://vitejs.dev/guide/performance.html)
- [Lighthouse CI Documentation](https://github.com/GoogleChrome/lighthouse-ci)

---

## Next Steps

1. **Execute First Baseline Run:**
   ```bash
   cd F:\Ebook\vibe-pdf-platform\Frontend
   npm run build
   npm run test:performance
   ```

2. **Review Results:** Check `playwright-report/index.html` for detailed metrics

3. **Run Lighthouse CI:**
   ```bash
   npm run test:lighthouse
   ```

4. **Update Baselines:** Replace "TBD" with actual measured values

5. **Set Up CI/CD:** Integrate tests into GitHub Actions workflow

6. **Establish Monitoring:** Configure ongoing performance tracking

---

## Summary

### Performance Test Files Created

| File | Location | Purpose |
|------|----------|---------|
| Core Web Vitals | `tests/performance/core-web-vitals.spec.ts` | LCP, FID, CLS metrics |
| Bundle Size | `tests/performance/bundle-size.spec.ts` | JS/CSS bundle budgets |
| Render Performance | `tests/performance/render-performance.spec.ts` | Component rendering |
| API Performance | `tests/performance/api-performance.spec.ts` | API response times |
| Navigation Performance | `tests/performance/navigation-performance.spec.ts` | Page load & transitions |

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| Lighthouse CI Config | `Frontend/lighthtrc.json` | Lighthouse budgets |
| Lighthouse Config | `F:/Ebook/lighthouse-config.js` | Root-level config |

### NPM Scripts Added

| Script | Command | Purpose |
|--------|---------|---------|
| `test:e2e` | `playwright test` | Run E2E tests |
| `test:e2e:ui` | `playwright test --ui` | E2E UI mode |
| `test:performance` | `playwright test tests/performance/` | Run performance tests |
| `test:lighthouse` | `lhci autorun` | Full Lighthouse CI |
| `test:lighthouse:collect` | `lhci collect` | Collect metrics only |
| `build:analyze` | `vite build --mode analyze` | Analyze bundle size |

**Note:** Current baselines are set as targets. Once initial test runs are completed, update the "Current" column with actual measured values and adjust targets based on 95th percentile performance.
