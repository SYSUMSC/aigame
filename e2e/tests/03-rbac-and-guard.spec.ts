import { expect, test } from '@playwright/test';
import { createApiContext, expectStatus, readJson } from '../utils/apiClient';
import { loginThroughUi, loginUser, registerUser } from '../utils/auth';
import { createTestUser } from '../utils/factory';
import { activateUser, banUser } from '../utils/mongo';

test.describe('03-权限与访问保护', () => {
  test('匿名用户访问管理页会跳转且调用管理接口返回401', async ({ page }) => {
    const api = await createApiContext();

    await page.goto('/admin/dashboard');
    await expect(page).toHaveURL(/\/login\?redirect=/);

    const response = await api.get('/api/admin/users');
    await expectStatus(response, 401);
    await api.dispose();
  });

  test('普通用户会被拦截在管理界面和管理接口之外', async ({ page }) => {
    const user = await createTestUser('rbac-normal');
    const api = await createApiContext();
    await expectStatus(await registerUser(api, user), 200);

    await loginThroughUi(page, user.email, user.password);
    await expect(page).toHaveURL(/\/$/);

    await page.goto('/admin/dashboard');
    await expect(page).toHaveURL(/\/$/);

    const apiResponse = await api.get('/api/admin/users');
    await expectStatus(apiResponse, 403);
    await api.dispose();
  });

  test('封禁用户在状态变更后会失去受保护接口访问权', async () => {
    const user = await createTestUser('rbac-banned');
    const api = await createApiContext();
    await expectStatus(await registerUser(api, user), 200);
    await activateUser(user.email);

    const loginResponse = await loginUser(api, user.email, user.password);
    await expectStatus(loginResponse, 200);
    await banUser(user.email);

    const meResponse = await api.get('/api/auth/me');
    await expectStatus(meResponse, 401);

    const body = await readJson<{ statusMessage?: string }>(meResponse);
    expect(body.statusMessage).toContain('banned');

    await api.dispose();
  });
});
