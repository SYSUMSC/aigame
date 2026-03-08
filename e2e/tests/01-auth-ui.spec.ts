import { expect, test } from '@playwright/test';
import { createApiContext, expectStatus } from '../utils/apiClient';
import { loginThroughUi, registerUser } from '../utils/auth';
import { createTestUser } from '../utils/factory';

test.describe('01-认证界面', () => {
  test('注册表单会校验最短密码长度', async ({ page }) => {
    const user = await createTestUser('register-validation');

    await page.goto('/register');
    await page.getByTestId('register-username').fill(user.username);
    await page.getByTestId('register-email').fill(user.email);
    await page.getByTestId('register-password').fill('12345');
    await page.getByTestId('register-submit').click();

    await expect(page.getByTestId('register-error')).toContainText('密码至少需要6位');
  });

  test('注册成功后保持登录态', async ({ page }) => {
    const user = await createTestUser('register-success');

    await page.goto('/register');
    await page.getByTestId('register-username').fill(user.username);
    await page.getByTestId('register-email').fill(user.email);
    await page.getByTestId('register-password').fill(user.password);
    await page.getByTestId('register-real-name').fill(user.realName);
    await page.getByTestId('register-student-id').fill(user.studentId);
    await page.getByTestId('register-phone-number').fill(user.phoneNumber);
    await page.getByTestId('register-education').selectOption(user.education);
    await page.getByTestId('register-submit').click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByTestId('nav-user-menu')).toContainText(user.username);
  });

  test('界面会展示重复注册冲突', async ({ page }) => {
    const api = await createApiContext();
    const existingUser = await createTestUser('register-duplicate');
    const registerResponse = await registerUser(api, existingUser);
    await expectStatus(registerResponse, 200);
    await api.dispose();

    const secondUser = await createTestUser('register-duplicate', {
      email: existingUser.email,
    });

    await page.goto('/register');
    await page.getByTestId('register-username').fill(secondUser.username);
    await page.getByTestId('register-email').fill(existingUser.email);
    await page.getByTestId('register-password').fill(secondUser.password);
    await page.getByTestId('register-submit').click();

    await expect(page.getByTestId('register-error')).toContainText('该邮箱已被注册');
  });

  test('未登录访问会跳转，且支持邮箱登录、退出和用户名登录', async ({ page }) => {
    const api = await createApiContext();
    const user = await createTestUser('login-flow');
    const registerResponse = await registerUser(api, user);
    await expectStatus(registerResponse, 200);
    await api.dispose();

    await page.goto('/teams');
    await expect(page).toHaveURL(/\/login\?redirect=/);

    await page.getByTestId('login-identifier').fill(user.email);
    await page.getByTestId('login-password').fill(user.password);
    await page.getByTestId('login-submit').click();
    await expect(page).toHaveURL(/\/teams$/);

    await page.getByTestId('nav-user-menu').hover();
    await page.getByTestId('nav-logout').click();
    await expect(page).toHaveURL(/\/login$/);

    await loginThroughUi(page, user.username, user.password);
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByTestId('nav-user-menu')).toContainText(user.username);
  });
});
