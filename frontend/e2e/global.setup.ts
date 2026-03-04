import { clerk, clerkSetup } from '@clerk/testing/playwright';
import { test as setup } from '@playwright/test';
import path from 'path';

setup.describe.configure({ mode: 'serial' });

const authFile = path.join(__dirname, '../playwright/.clerk/user.json');

setup('initialize clerk', async () => {
  await clerkSetup();

  if (!process.env.E2E_CLERK_USER_USERNAME || !process.env.E2E_CLERK_USER_PASSWORD) {
    throw new Error(
      'E2E_CLERK_USER_USERNAME and E2E_CLERK_USER_PASSWORD must be set. ' +
        'Create a test user in your Clerk dashboard with password auth enabled.'
    );
  }
});

setup('authenticate', async ({ page }) => {
  await page.goto('/');
  await clerk.signIn({
    page,
    signInParams: {
      strategy: 'password',
      identifier: process.env.E2E_CLERK_USER_USERNAME!,
      password: process.env.E2E_CLERK_USER_PASSWORD!,
    },
  });
  await page.goto('/dashboard');
  await page.waitForSelector('h1');
  await page.context().storageState({ path: authFile });
});
