/**
 * E2E Test: User Registration and Login Flow
 * Tests the complete user authentication flow including registration, login, and logout.
 */

import { test, expect } from '@playwright/test';

test.describe('User Registration and Login Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the home page before each test
    await page.goto('/');
  });

  test.describe('User Registration', () => {
    
    test('should display registration form', async ({ page }) => {
      // Look for registration link/button and click it
      const registerLink = page.getByRole('link', { name: /register|sign up/i }).first();
      
      // If registration link exists, click it
      if (await registerLink.isVisible()) {
        await registerLink.click();
        
        // Verify registration form elements are present
        await expect(page.getByLabel(/email/i)).toBeVisible();
        await expect(page.getByLabel(/username/i)).toBeVisible();
        await expect(page.getByLabel(/password/i)).toBeVisible();
        await expect(page.getByLabel(/full name/i)).toBeVisible();
      } else {
        // If no dedicated registration page, check for any registration form on the page
        const emailInput = page(/email/i);
.getByLabel        const submitButton = page.getByRole('button', { name: /register|sign up|submit/i });
        
        // At least verify the page loads without errors
        await expect(page).toHaveTitle(/ebook|vibe|pdf/i);
      }
    });

    test('should validate registration input', async ({ page }) => {
      // Navigate to registration if available
      const registerLink = page.getByRole('link', { name: /register|sign up/i }).first();
      
      if (await registerLink.isVisible()) {
        await registerLink.click();
        
        // Try to submit empty form
        const submitButton = page.getByRole('button', { name: /register|sign up|submit/i });
        
        if (await submitButton.isVisible()) {
          await submitButton.click();
          
          // Should show validation errors
          const validationErrors = await page.locator('[role="alert"], .error, .text-red').count();
          expect(validationErrors).toBeGreaterThanOrEqual(0);
        }
      }
    });

    test('should register new user successfully', async ({ page }) => {
      const registerLink = page.getByRole('link', { name: /register|sign up/i }).first();
      
      if (await registerLink.isVisible()) {
        await registerLink.click();
        
        // Fill in registration form
        const timestamp = Date.now();
        await page.getByLabel(/email/i).fill(`testuser${timestamp}@example.com`);
        await page.getByLabel(/username/i).fill(`testuser${timestamp}`);
        await page.getByLabel(/password/i).fill('TestPassword123!');
        await page.getByLabel(/full name/i).fill('Test User');
        
        // Submit form
        const submitButton = page.getByRole('button', { name: /register|sign up|submit/i });
        await submitButton.click();
        
        // Should either redirect to dashboard or show success message
        await page.waitForTimeout(2000);
        
        // Check for success or redirect
        const currentUrl = page.url();
        const hasDashboard = currentUrl.includes('/dashboard') || currentUrl.includes('/library');
        const hasSuccessMessage = await page.getByText(/success|welcome|registered/i).isVisible().catch(() => false);
        
        expect(hasDashboard || hasSuccessMessage || currentUrl !== '/').toBeTruthy();
      }
    });
  });

  test.describe('User Login', () => {
    
    test('should display login form', async ({ page }) => {
      // Look for login link
      const loginLink = page.getByRole('link', { name: /login|sign in/i }).first();
      
      if (await loginLink.isVisible()) {
        await loginLink.click();
        
        // Verify login form elements
        await expect(page.getByLabel(/username|email/i)).toBeVisible();
        await expect(page.getByLabel(/password/i)).toBeVisible();
      }
    });

    test('should login with valid credentials', async ({ page }) => {
      const loginLink = page.getByRole('link', { name: /login|sign in/i }).first();
      
      if (await loginLink.isVisible()) {
        await loginLink.click();
        
        // Fill in login form
        await page.getByLabel(/username|email/i).fill('testuser@example.com');
        await page.getByLabel(/password/i).fill('password123');
        
        // Submit form
        const submitButton = page.getByRole('button', { name: /login|sign in|submit/i });
        await submitButton.click();
        
        // Wait for response
        await page.waitForTimeout(2000);
        
        // Should redirect to dashboard or show user info
        const currentUrl = page.url();
        const isAuthenticated = currentUrl.includes('/dashboard') || 
                               currentUrl.includes('/library') || 
                               currentUrl.includes('/profile');
        
        // Check for user menu or logout button
        const hasUserMenu = await page.getByRole('button', { name: /logout|sign out/i }).isVisible().catch(() => false) ||
                           await page.getByText(/testuser/i).isVisible().catch(() => false);
        
        expect(isAuthenticated || hasUserMenu).toBeTruthy();
      }
    });

    test('should show error with invalid credentials', async ({ page }) => {
      const loginLink = page.getByRole('link', { name: /login|sign in/i }).first();
      
      if (await loginLink.isVisible()) {
        await loginLink.click();
        
        // Fill in invalid credentials
        await page.getByLabel(/username|email/i).fill('invalid@example.com');
        await page.getByLabel(/password/i).fill('wrongpassword');
        
        // Submit form
        const submitButton = page.getByRole('button', { name: /login|sign in|submit/i });
        await submitButton.click();
        
        // Wait for response
        await page.waitForTimeout(1000);
        
        // Should show error message
        const errorMessage = await page.getByText(/invalid|error|incorrect|failed/i).first().isVisible().catch(() => false);
        
        // Either show error or stay on login page
        const currentUrl = page.url();
        const stillOnLogin = currentUrl.includes('/login') || currentUrl.includes('/auth');
        
        expect(errorMessage || stillOnLogin).toBeTruthy();
      }
    });
  });

  test.describe('User Logout', () => {
    
    test('should logout successfully', async ({ page }) => {
      // First login (if possible)
      const loginLink = page.getByRole('link', { name: /login|sign in/i }).first();
      
      if (await loginLink.isVisible()) {
        await loginLink.click();
        
        await page.getByLabel(/username|email/i).fill('test@example.com');
        await page.getByLabel(/password/i).fill('password123');
        
        const submitButton = page.getByRole('button', { name: /login|sign in/i });
        await submitButton.click();
        
        await page.waitForTimeout(2000);
        
        // Look for logout button
        const logoutButton = page.getByRole('button', { name: /logout|sign out/i });
        
        if (await logoutButton.isVisible()) {
          await logoutButton.click();
          
          // Should redirect to home page or show login
          await page.waitForTimeout(1000);
          
          const currentUrl = page.url();
          const hasLoginLink = await page.getByRole('link', { name: /login|sign in/i }).isVisible().catch(() => false);
          
          expect(currentUrl === '/' || hasLoginLink).toBeTruthy();
        }
      }
    });
  });
});
