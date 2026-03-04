import { setupClerkTestingToken } from '@clerk/testing/playwright';
import { test, expect } from '@playwright/test';

test.describe('Landing page', () => {
  test('renders hero section with title and CTAs', async ({ page }) => {
    await setupClerkTestingToken({ page });
    await page.goto('/');

    await expect(page.locator('h1')).toContainText('DualStack');
    await expect(page.getByRole('link', { name: 'Get Started' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign In' })).toBeVisible();
  });

  test('shows feature cards', async ({ page }) => {
    await setupClerkTestingToken({ page });
    await page.goto('/');

    await expect(page.getByText('Authentication')).toBeVisible();
    await expect(page.getByText('Database')).toBeVisible();
    await expect(page.getByText('Billing')).toBeVisible();
  });

  test('Get Started link navigates to sign-up', async ({ page }) => {
    await setupClerkTestingToken({ page });
    await page.goto('/');

    await page.getByRole('link', { name: 'Get Started' }).click();
    await expect(page).toHaveURL(/\/sign-up/);
  });

  test('Sign In link navigates to sign-in', async ({ page }) => {
    await setupClerkTestingToken({ page });
    await page.goto('/');

    await page.getByRole('link', { name: 'Sign In' }).click();
    await expect(page).toHaveURL(/\/sign-in/);
  });
});
