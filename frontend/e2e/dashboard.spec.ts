import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('renders dashboard overview', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.getByText('Welcome to your DualStack dashboard')).toBeVisible();
  });

  test('shows stat cards', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page.getByText('Items')).toBeVisible();
    await expect(page.getByText('Subscription')).toBeVisible();
    await expect(page.getByText('Credits')).toBeVisible();
  });

  test('sidebar navigation works', async ({ page }) => {
    await page.goto('/dashboard');

    await page.getByRole('link', { name: 'Items' }).click();
    await expect(page).toHaveURL(/\/items/);
    await expect(page.locator('h1')).toContainText('Items');

    await page.getByRole('link', { name: 'Billing' }).click();
    await expect(page).toHaveURL(/\/billing/);
    await expect(page.locator('h1')).toContainText('Billing');

    await page.getByRole('link', { name: 'Settings' }).click();
    await expect(page).toHaveURL(/\/settings/);
    await expect(page.locator('h1')).toContainText('Settings');

    await page.getByRole('link', { name: 'Dashboard' }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
