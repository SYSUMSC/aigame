import { defineConfig } from '@playwright/test';

// 统一测试入口地址，默认指向本地容器编排暴露的网站服务。
const baseURL = process.env.E2E_BASE_URL || `http://127.0.0.1:${process.env.WEBAPP_HOST_PORT || '33000'}`;

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: 1,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    headless: true,
  },
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
      },
    },
  ],
});
