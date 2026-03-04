import { test, expect } from '@playwright/test';

test.describe('Billing page', () => {
  test('renders plan cards with prices', async ({ page }) => {
    await page.goto('/billing');

    await expect(page.locator('h1')).toContainText('Billing');
    await expect(page.getByText('$0/mo')).toBeVisible();
    await expect(page.getByText('$10/mo')).toBeVisible();
  });

  test('shows plan features and button states', async ({ page }) => {
    await page.goto('/billing');

    // Free plan features
    await expect(page.getByText('1 project')).toBeVisible();
    await expect(page.getByText('Basic support')).toBeVisible();

    // Pro plan features
    await expect(page.getByText('Unlimited projects')).toBeVisible();
    await expect(page.getByText('Priority support')).toBeVisible();

    // Button states
    await expect(page.getByRole('button', { name: 'Current Plan' })).toBeDisabled();
    await expect(page.getByRole('button', { name: 'Subscribe' })).toBeEnabled();
  });
});
