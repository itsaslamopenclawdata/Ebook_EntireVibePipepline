# Visual Regression Testing Guide

> Complete guide to running, maintaining, and updating visual regression tests for the Vibe PDF Platform frontend.

---

## Table of Contents

- [Overview](#overview)
- [Test Suite Structure](#test-suite-structure)
- [Running Tests](#running-tests)
- [Updating Baselines](#updating-baselines)
- [Writing New Tests](#writing-new-tests)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

---

## Overview

### What is Visual Regression Testing?

Visual regression testing automatically captures screenshots of your UI and compares them against previously approved "baseline" screenshots. Any differences are highlighted for review, helping catch unintended visual changes.

### Benefits

- **Catch UI bugs early**: Detect layout shifts, color changes, spacing issues
- **Prevent regressions**: Ensure design consistency across releases
- **Document UI state**: Visual history of component appearances
- **Cross-browser testing**: Verify consistency across browsers and devices
- **Responsive testing**: Validate mobile, tablet, desktop layouts

### Our Test Coverage

The visual test suite includes **7 comprehensive test files** covering:

| Test File | Coverage | Scenarios |
|-----------|----------|-----------|
| `header-visual.spec.ts` | Header component | Auth states, dropdowns, mobile menu, notifications, viewports |
| `bookcard-visual.spec.ts` | BookCard component | All statuses, loading, compact mode, input methods, hover states |
| `dashboard-visual.spec.ts` | Dashboard view | Empty/loading/error states, filters, grid/list view, pagination |
| `mobile-visual.spec.ts` | Mobile responsive | 5 viewport sizes, mobile menu, FAB, touch interactions, landscape |
| `ui-components-visual.spec.ts` | Base components | Buttons, inputs, selects, modals, toasts, cards, toggles |
| `book-creation-visual.spec.ts` | Creation flow | 3-step wizard, form validation, progress tracking, all states |
| `accessibility-visual.spec.ts` | Accessibility features | Focus states, ARIA labels, high contrast, screen reader support |

**Total Test Count**: 80+ visual test scenarios

---

## Test Suite Structure

```
Frontend/
├── tests/
│   └── visual/
│       ├── header-visual.spec.ts          # Header component tests
│       ├── bookcard-visual.spec.ts        # BookCard component tests
│       ├── dashboard-visual.spec.ts       # Dashboard view tests
│       ├── mobile-visual.spec.ts          # Mobile responsive tests
│       ├── ui-components-visual.spec.ts   # Base UI components
│       ├── book-creation-visual.spec.ts   # Book creation flow
│       └── accessibility-visual.spec.ts   # Accessibility features
├── playwright.config.ts                    # Playwright configuration
└── test-results/
    ├── visual-baseline/                    # Approved baseline screenshots
    └── visual-comparison/                  # Diff images (on failure)
```

### Screenshot Threshold Configuration

Located in `playwright.config.ts`:

```typescript
expect: {
  toHaveScreenshot: {
    maxDiffPixels: 100,        // Maximum pixels that can differ
    threshold: 0.2,            // 0.2% difference allowed
  },
  toMatchSnapshot: {
    maxDiffPixels: 100,
    threshold: 0.2,
  },
}
```

---

## Running Tests

### Prerequisites

```bash
# Install dependencies (if not already installed)
cd Frontend
npm install

# Install Playwright browsers (first time only)
npx playwright install
```

### Run All Visual Tests

```bash
# Run visual regression tests
npm run test:visual

# Or using Playwright directly with visual flag
VISUAL_REGRESSION=true npx playwright test
```

### Run Specific Test File

```bash
# Run only header tests
npx playwright tests/visual/header-visual.spec.ts

# Run only mobile tests
npx playwright tests/visual/mobile-visual.spec.ts
```

### Run on Specific Browser

```bash
# Chrome
npx playwright test --project=chromium

# Firefox
npx playwright test --project=firefox

# Safari (WebKit)
npx playwright test --project=webkit

# Mobile Chrome
npx playwright test --project="Mobile Chrome"
```

### Run with Update Mode

```bash
# Update all baselines (use carefully!)
npx playwright test --update-screenshot

# Update specific test file
npx playwright tests/visual/header-visual.spec.ts --update-screenshot
```

### View Test Report

After tests run, view the HTML report:

```bash
npx playwright show-report
```

---

## Updating Baselines

### When to Update Baselines

**DO update** when:
- Intentional design changes (color, spacing, layout)
- New features or UI components
- Fixing visual bugs
- Responsive design improvements
- Dark mode implementation

**DON'T update** when:
- unintended visual regressions
- accidental layout shifts
- temporary failures
- dynamic content changes (time, dates, etc.)

### Update Process

#### Step 1: Review Failed Tests

```bash
# Run tests to see failures
npx playwright test
```

#### Step 2: Investigate Differences

Playwright generates three images for each failure:

1. **Expected**: Baseline screenshot
2. **Actual**: Current screenshot
3. **Diff**: Highlighted differences

View these in:
- HTML report (`npx playwright show-report`)
- Directly in `test-results/` directory

#### Step 3: Decide Action

**If difference is intentional**:
```bash
# Update specific test baseline
npx playwright test --update-screenshot tests/visual/header-visual.spec.ts
```

**If difference is a bug**:
1. Fix the underlying issue
2. Re-run tests
3. Baseline should match automatically

**If difference is flaky (dynamic content)**:
See [Troubleshooting](#troubleshooting) below.

### Committing Updated Baselines

```bash
# Add updated baselines to git
git add test-results/visual-baseline/

# Commit with descriptive message
git commit -m "test(visual): update header baseline for new logo design

- Updated header-logged-in.png
- Updated header-dropdown-open.png
- Related feature: Add new branding"
```

---

## Writing New Tests

### Test Template

```typescript
import { test, expect } from '@playwright/test';

test.describe('ComponentName - Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Mock data, authentication, etc.
    await page.goto('/');
  });

  test('should display component in default state', async ({ page }) => {
    // Arrange: Set up test conditions
    await page.goto('/component-test');

    // Act: Trigger any state changes if needed

    // Assert: Capture screenshot
    await expect(page.locator('[data-testid="component"]'))
      .toHaveScreenshot('component-default.png');
  });
});
```

### Screenshot Best Practices

#### 1. Target Specific Elements

```typescript
// Good: Screenshot specific component
await expect(page.locator('[data-testid="book-card"]'))
  .toHaveScreenshot('bookcard.png');

// Avoid: Screenshot entire page (too brittle)
await expect(page.locator('body')).toHaveScreenshot('page.png');
```

#### 2. Wait for Stability

```typescript
// Wait for animations to complete
await page.waitForTimeout(300);

// Wait for network idle
await page.waitForLoadState('networkidle');

// Wait for specific element to be visible
await page.waitForSelector('[data-testid="component-loaded"]');
```

#### 3. Mask Dynamic Content

```typescript
// Mask time-sensitive content
await expect(page.locator('[data-testid="book-card"]'))
  .toHaveScreenshot('bookcard.png', {
    mask: [page.locator('[data-testid="timestamp"]')],
  });
```

#### 4. Adjust Thresholds for Tolerance

```typescript
// Strict matching for static components
await expect(page.locator('[data-testid="logo"]'))
  .toHaveScreenshot('logo.png', {
    threshold: 0.0, // No difference allowed
  });

// More tolerance for dynamic content
await expect(page.locator('[data-testid="user-avatar"]'))
  .toHaveScreenshot('avatar.png', {
    threshold: 0.5, // 0.5% difference allowed
    maxDiffPixels: 200,
  });
```

### Test Naming Conventions

```typescript
// Screenshot filenames should follow pattern:
// {component}-{state}-{variant}.png

await expect(card).toHaveScreenshot('bookcard-pending.png');
await expect(card).toHaveScreenshot('bookcard-processing.png');
await expect(card).toHaveScreenshot('bookcard-completed.png');
await expect(card).toHaveScreenshot('bookcard-compact.png');
await expect(card).toHaveScreenshot('bookcard-hover.png');
await expect(card).toHaveScreenshot('bookcard-mobile.png');
```

---

## Best Practices

### 1. Isolate Components

Test components in isolation when possible:

```typescript
test('should display button variants', async ({ page }) => {
  await page.goto('/test/components-buttons');

  await expect(page.locator('[data-testid="button-variants"]'))
    .toHaveScreenshot('button-variants.png');
});
```

### 2. Use Test Data Attributes

Add `data-testid` attributes for reliable selectors:

```tsx
// In React components
<button data-testid="submit-button">Submit</button>
<div data-testid="book-card">{/* ... */}</div>
```

### 3. Mock External Dependencies

Mock APIs, WebSocket, dates, etc.:

```typescript
// Mock API
await page.route('**/api/books', (route) => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ books: mockBooks }),
  });
});

// Mock dates
await page.addInitScript(() => {
  const mockDate = new Date('2024-01-15T10:00:00Z');
  Date.now = () => mockDate.getTime();
});
```

### 4. Test Multiple Viewports

```typescript
const VIEWPORTS = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1280, height: 720 },
};

for (const [name, viewport] of Object.entries(VIEWPORTS)) {
  test(`should display on ${name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    // ... test code
  });
}
```

### 5. Test Interactive States

```typescript
test('should display hover state', async ({ page }) => {
  const card = page.locator('[data-testid="book-card"]');
  await card.hover();
  await page.waitForTimeout(200); // Wait for CSS transition

  await expect(card).toHaveScreenshot('card-hover.png');
});
```

### 6. Test Dark Mode (if applicable)

```typescript
test('should display in dark mode', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto('/');

  await expect(page.locator('body')).toHaveScreenshot('dark-mode.png');
});
```

---

## Troubleshooting

### Issue: Tests Flaky Due to Dynamic Content

**Problem**: Timestamps, random IDs, or avatars cause failures.

**Solutions**:

1. **Mask dynamic elements**:
```typescript
await expect(page.locator('[data-testid="book-card"]'))
  .toHaveScreenshot('card.png', {
    mask: [
      page.locator('[data-testid="timestamp"]'),
      page.locator('[data-testid="random-id"]'),
    ],
  });
```

2. **Mock the data**:
```typescript
await page.addInitScript(() => {
  (window as any).__MOCK_DATE__ = new Date('2024-01-15').toISOString();
});
```

3. **Use fixed test data**:
```typescript
const MOCK_BOOKS = [
  { id: 'test-1', title: 'Test Book', createdAt: '2024-01-15T10:00:00Z' },
];
```

### Issue: Animations Cause Inconsistencies

**Problem**: Screenshots capture animation at different frames.

**Solutions**:

1. **Disable animations**:
```typescript
await page.addInitScript(() => {
  document.body.classList.add('test-disable-animations');
});

// In CSS
body.test-disable-animations *,
body.test-disable-animations *::before,
body.test-disable-animations *::after {
  animation-duration: 0s !important;
  transition-duration: 0s !important;
}
```

2. **Wait for animations**:
```typescript
await page.click('[data-testid="button"]');
await page.waitForTimeout(300); // Wait for transition to complete
```

### Issue: Font Rendering Differences

**Problem**: Fonts render differently across OS/browsers.

**Solutions**:

1. **Use web fonts consistently**:
```typescript
await page.addInitScript(() => {
  document.fonts.ready.then(() => {
    // Fonts loaded
  });
});
```

2. **Wait for fonts**:
```typescript
await page.goto('/', { waitUntil: 'networkidle' });
await page.waitForFunction(() => document.fonts.ready);
```

### Issue: Layout Shifts During Screenshot

**Problem**: Elements move while screenshot is captured.

**Solutions**:

1. **Wait for stable state**:
```typescript
await page.waitForLoadState('domcontentloaded');
await page.waitForLoadState('networkidle');

// Additional wait for lazy-loaded content
await page.waitForTimeout(500);
```

2. **Stabilize layout**:
```typescript
await page.evaluate(() => {
  // Force layout recalculation
  document.body.offsetHeight;
});
```

### Issue: Color Differences Across Browsers

**Problem**: Same colors appear slightly different in Chrome vs Firefox.

**Solutions**:

1. **Increase threshold for color-heavy tests**:
```typescript
await expect(page.locator('[data-testid="colorful-component"]'))
  .toHaveScreenshot('colorful.png', {
    threshold: 0.3, // Allow 0.3% color difference
  });
```

2. **Test color separately** (not via screenshots):
```typescript
test('should have correct primary color', async ({ page }) => {
  const color = await page.locator('[data-testid="primary-button"]')
    .evaluate(el => getComputedStyle(el).backgroundColor);

  expect(color).toBe('rgb(255, 107, 107)');
});
```

---

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/visual-regression.yml`:

```yaml
name: Visual Regression Tests

on:
  pull_request:
    paths:
      - 'Frontend/src/**'
      - 'Frontend/tests/visual/**'
  push:
    branches: [main]

jobs:
  visual-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        working-directory: ./Frontend
        run: npm ci

      - name: Install Playwright browsers
        working-directory: ./Frontend
        run: npx playwright install --with-deps

      - name: Run visual regression tests
        working-directory: ./Frontend
        env:
          VISUAL_REGRESSION: true
        run: npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: visual-test-results
          path: Frontend/test-results/
          retention-days: 30

      - name: Upload baseline screenshots
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: visual-baselines
          path: Frontend/test-results/visual-baseline/
          retention-days: 30
```

### Handling Baseline Updates in PRs

When visual tests fail in a PR:

1. **Review the diff** in the Actions artifacts
2. **Comment on PR** with decision:
   - `/approve-visual` if differences are intentional
   - `/fix-visual` if differences are bugs
3. **Maintainer updates** baselines after approval

### Preventing False Positives

```yaml
# Allow threshold adjustments in CI
- name: Run visual tests with lenient threshold
  env:
    PLAYWRIGHT_ALLOW_DIFF: "0.3%"  # More lenient in CI
  run: npx playwright test
```

---

## Quick Reference Commands

```bash
# Run all visual tests
npx playwright test

# Run with baseline update
npx playwright test --update-screenshot

# Run specific browser
npx playwright test --project=chromium

# Run specific file
npx playwright test tests/visual/header-visual.spec.ts

# Run with debug mode
npx playwright test --debug

# View HTML report
npx playwright show-report

# Install browsers
npx playwright install

# Install specific browser only
npx playwright install chromium
```

---

## Test File Count Summary

| Test File | Test Scenarios |
|-----------|----------------|
| header-visual.spec.ts | 10 |
| bookcard-visual.spec.ts | 14 |
| dashboard-visual.spec.ts | 13 |
| mobile-visual.spec.ts | 13 |
| ui-components-visual.spec.ts | 22 |
| book-creation-visual.spec.ts | 16 |
| accessibility-visual.spec.ts | 14 |
| **Total** | **102 scenarios** |

---

## Additional Resources

- [Playwright Screenshot Testing Docs](https://playwright.dev/docs/screenshots)
- [Playwright Visual Comparison Docs](https://playwright.dev/docs/test-snapshots)
- [Visual Regression Testing Best Practices](https://www.smashingmagazine.com/2022/02/comprehensive-guide-visual-regression-testing/)

---

## Support

For questions or issues with visual tests:

1. Check this guide's [Troubleshooting](#troubleshooting) section
2. Review Playwright documentation
3. Check existing GitHub issues
4. Create new issue with:
   - Test file and scenario
   - Screenshot diffs (expected, actual, diff)
   - Browser and viewport info
   - Error messages
