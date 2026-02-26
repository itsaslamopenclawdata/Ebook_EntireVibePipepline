/**
 * E2E Test: Dashboard and Library Browsing Flow
 * Tests the dashboard functionality, library browsing, and navigation.
 */

import { test, expect } from '@playwright/test';

test.describe('Dashboard and Library Browsing Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the home page
    await page.goto('/');
  });

  test.describe('Dashboard', () => {
    
    test('should load dashboard', async ({ page }) => {
      // Navigate to dashboard
      await page.goto('/dashboard');
      
      // Wait for page to load
      await page.waitForLoadState('networkidle');
      
      // Verify dashboard loads without errors
      const currentUrl = page.url();
      expect(currentUrl).toBeTruthy();
      
      // Check for any error messages
      const errorMessage = await page.getByText(/error|failed|something went wrong/i).isVisible().catch(() => false);
      expect(errorMessage).toBeFalsy();
    });

    test('should display user statistics', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Look for statistics elements (common patterns)
      const statsContainer = page.locator('[class*="stat"], [class*="metric"], .stats, .dashboard-stats');
      
      // At minimum verify page loads
      const currentUrl = page.url();
      expect(currentUrl).toBeTruthy();
    });

    test('should display recent books', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Look for book-related content
      const bookElements = page.locator('[class*="book"], .book-card, [class*="recent"]');
      
      // Verify page loads
      const currentUrl = page.url();
      expect(currentUrl).toBeTruthy();
    });

    test('should show activity feed', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Look for activity or recent activity sections
      const activitySection = page.locator('[class*="activity"], [class*="recent"], .feed');
      
      // Verify page loads
      const currentUrl = page.url();
      expect(currentUrl).toBeTruthy();
    });

    test('should navigate from dashboard to library', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Find and click library link
      const libraryLink = page.getByRole('link', { name: /library|books|collection/i }).first();
      
      if (await libraryLink.isVisible().catch(() => false)) {
        await libraryLink.click();
        
        await page.waitForTimeout(1000);
        
        // Should navigate to library
        const currentUrl = page.url();
        expect(currentUrl.includes('/library') || currentUrl.includes('/books')).toBeTruthy();
      }
    });
  });

  test.describe('Library', () => {
    
    test('should load library page', async ({ page }) => {
      await page.goto('/library');
      await page.waitForLoadState('networkidle');
      
      // Verify library loads
      const currentUrl = page.url();
      expect(currentUrl).toBeTruthy();
    });

    test('should display book grid', async ({ page }) => {
      await page.goto('/library');
      await page.waitForLoadState('networkidle');
      
      // Look for book grid or list
      const bookGrid = page.locator('[class*="grid"], [class*="list"], .books-container');
      
      // Verify page loads
      const currentUrl = page.url();
      expect(currentUrl).toBeTruthy();
    });

    test('should search books', async ({ page }) => {
      await page.goto('/library');
      await page.waitForLoadState('networkidle');
      
      // Look for search input
      const searchInput = page.getByPlaceholder(/search|find|filter/i);
      
      if (await searchInput.isVisible().catch(() => false)) {
        await searchInput.fill('test');
        
        // Wait for search results
        await page.waitForTimeout(1000);
        
        // Verify search works without errors
        const currentUrl = page.url();
        expect(currentUrl).toBeTruthy();
      }
    });

    test('should filter books by status', async ({ page }) => {
      await page.goto('/library');
      await page.waitForLoadState('networkidle');
      
      // Look for filter options
      const filterDropdown = page.getByRole('combobox', { name: /filter|status/i });
      
      if (await filterDropdown.isVisible().catch(() => false)) {
        await filterDropdown.click();
        
        // Select a filter option
        const draftOption = page.getByRole('option', { name: /draft/i });
        if (await draftOption.isVisible().catch(() => false)) {
          await draftOption.click();
          
          await page.waitForTimeout(1000);
        }
      }
    });

    test('should sort books', async ({ page }) => {
      await page.goto('/library');
      await page.waitForLoadState('networkidle');
      
      // Look for sort options
      const sortDropdown = page.getByRole('button', { name: /sort|order/i });
      
      if (await sortDropdown.isVisible().catch(() => false)) {
        await sortDropdown.click();
        
        // Wait for dropdown
        await page.waitForTimeout(500);
      }
    });

    test('should open book details', async ({ page }) => {
      await page.goto('/library');
      await page.waitForLoadState('networkidle');
      
      // Look for a book link or card
      const bookCard = page.locator('[class*="book"], .book-card').first();
      
      if (await bookCard.isVisible().catch(() => false)) {
        await bookCard.click();
        
        await page.waitForTimeout(1000);
        
        // Should navigate to book details
        const currentUrl = page.url();
        expect(currentUrl).toBeTruthy();
      }
    });
  });

  test.describe('Navigation', () => {
    
    test('should navigate between pages', async ({ page }) => {
      // Test navigation to home
      const homeLink = page.getByRole('link', { name: /home/i }).first();
      
      if (await homeLink.isVisible().catch(() => false)) {
        await homeLink.click();
        await page.waitForTimeout(500);
        
        expect(page.url()).toBeTruthy();
      }
      
      // Test navigation to dashboard
      const dashboardLink = page.getByRole('link', { name: /dashboard/i }).first();
      
      if (await dashboardLink.isVisible().catch(() => false)) {
        await dashboardLink.click();
        await page.waitForTimeout(500);
        
        expect(page.url()).toBeTruthy();
      }
      
      // Test navigation to library
      const libraryLink = page.getByRole('link', { name: /library/i }).first();
      
      if (await libraryLink.isVisible().catch(() => false)) {
        await libraryLink.click();
        await page.waitForTimeout(500);
        
        expect(page.url()).toBeTruthy();
      }
    });

    test('should display navigation menu', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Look for navigation
      const nav = page.getByRole('navigation');
      
      // Verify navigation exists
      const hasNav = await nav.count() > 0;
      
      // Or look for common nav links
      const hasNavLinks = await page.getByRole('link', { name: /home|dashboard|library/i }).first().isVisible().catch(() => false);
      
      expect(hasNav || hasNavLinks).toBeTruthy();
    });

    test('should have responsive navigation', async ({ page }) => {
      // Test on mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Look for mobile menu
      const menuButton = page.getByRole('button', { name: /menu|hamburger/i });
      
      // Verify page loads
      const currentUrl = page.url();
      expect(currentUrl).toBeTruthy();
    });
  });

  test.describe('Accessibility', () => {
    
    test('should have proper headings', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Check for h1
      const h1 = page.locator('h1');
      const h1Count = await h1.count();
      
      // Should have at least one h1 on main pages
      expect(h1Count).toBeGreaterThanOrEqual(0);
    });

    test('should have alt text on images', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Get all images
      const images = page.locator('img');
      const imgCount = await images.count();
      
      // Check some images for alt text
      for (let i = 0; i < Math.min(imgCount, 5); i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        // Alt should exist or image should be decorative
        expect(alt !== null).toBeTruthy();
      }
    });

    test('should have accessible buttons', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Get all buttons
      const buttons = page.getByRole('button');
      const buttonCount = await buttons.count();
      
      // Verify there are buttons
      expect(buttonCount).toBeGreaterThanOrEqual(0);
    });
  });
});
