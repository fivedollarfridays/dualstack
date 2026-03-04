import { defineConfig, devices } from '@playwright/test';
import path from 'path';

const PORT = process.env.PORT || 3000;
const baseURL = `http://localhost:${PORT}`;

export default defineConfig({
  testDir: path.join(__dirname, 'e2e'),
  outputDir: 'test-results/',
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  workers: 1,

  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  webServer: {
    command: 'npm run dev',
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },

  projects: [
    {
      name: 'global setup',
      testMatch: /global\.setup\.ts/,
    },
    {
      name: 'public',
      testMatch: /landing\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['global setup'],
    },
    {
      name: 'authenticated',
      testMatch: /(?<!landing)\.spec\.ts$/,
      testIgnore: /landing\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.clerk/user.json',
      },
      dependencies: ['global setup'],
    },
  ],
});
