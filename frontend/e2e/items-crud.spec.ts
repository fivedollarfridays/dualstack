import { test, expect } from '@playwright/test';

test.describe('Items CRUD', () => {
  test.describe.configure({ mode: 'serial' });

  const testTitle = `E2E Test Item ${Date.now()}`;
  const testDescription = 'Created by Playwright E2E test';
  const updatedTitle = `${testTitle} (edited)`;

  test('create a new item', async ({ page }) => {
    await page.goto('/items');

    await page.getByRole('button', { name: 'New Item' }).click();
    await expect(page).toHaveURL(/\/items\/new/);

    await page.getByLabel('Title').fill(testTitle);
    await page.getByLabel('Description').fill(testDescription);
    await page.getByLabel('Status').selectOption('active');

    await page.getByRole('button', { name: 'Create' }).click();

    await expect(page).toHaveURL(/\/items$/, { timeout: 10_000 });
    await expect(page.getByText(testTitle)).toBeVisible();
  });

  test('edit the item', async ({ page }) => {
    await page.goto('/items');
    await expect(page.getByText(testTitle)).toBeVisible();

    const itemCard = page.locator('[class*="rounded-lg"]').filter({ hasText: testTitle }).first();
    await itemCard.getByRole('button', { name: 'Edit' }).click();

    await expect(page).toHaveURL(/\/items\/.+/);
    await expect(page.locator('h1')).toContainText('Edit Item');

    const titleInput = page.getByLabel('Title');
    await titleInput.clear();
    await titleInput.fill(updatedTitle);

    await page.getByRole('button', { name: 'Update' }).click();

    await expect(page).toHaveURL(/\/items$/, { timeout: 10_000 });
    await expect(page.getByText(updatedTitle)).toBeVisible();
  });

  test('delete the item', async ({ page }) => {
    await page.goto('/items');
    await expect(page.getByText(updatedTitle)).toBeVisible();

    page.on('dialog', (dialog) => dialog.accept());

    const itemCard = page.locator('[class*="rounded-lg"]').filter({ hasText: updatedTitle }).first();
    await itemCard.getByRole('button', { name: 'Delete' }).click();

    await expect(page.getByText(updatedTitle)).not.toBeVisible({ timeout: 10_000 });
  });
});
