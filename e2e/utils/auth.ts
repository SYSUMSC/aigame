import { expect, type APIRequestContext, type Page } from '@playwright/test';
import type { TestUser } from './factory';
import { createApiContext, expectStatus, readJson } from './apiClient';
import { activateUser } from './mongo';
import { adminAccount } from '../fixtures/accounts';

// 调用注册接口创建测试用户。
export async function registerUser(api: APIRequestContext, user: TestUser) {
  return api.post('/api/auth/register', {
    data: {
      username: user.username,
      email: user.email,
      password: user.password,
      realName: user.realName,
      studentId: user.studentId,
      phoneNumber: user.phoneNumber,
      education: user.education,
    },
  });
}

// 使用邮箱或用户名执行登录。
export async function loginUser(api: APIRequestContext, identifier: string, password: string) {
  return api.post('/api/auth/login', {
    data: {
      identifier,
      password,
    },
  });
}

// 创建已登录的管理员接口上下文。
export async function createAdminApiContext(): Promise<APIRequestContext> {
  const api = await createApiContext();
  const response = await loginUser(api, adminAccount.username, adminAccount.password);
  await expectStatus(response, 200);
  return api;
}

// 创建已注册用户的接口上下文，并按需直接激活账号。
export async function createRegisteredUserApiContext(user: TestUser, options?: { activate?: boolean }): Promise<APIRequestContext> {
  const api = await createApiContext();
  const registerResponse = await registerUser(api, user);
  await expectStatus(registerResponse, 200);

  if (options?.activate) {
    await activateUser(user.email);
  }

  const loginResponse = await loginUser(api, user.email, user.password);
  await expectStatus(loginResponse, 200);
  return api;
}

// 通过界面完成一次登录流程。
export async function loginThroughUi(page: Page, identifier: string, password: string): Promise<void> {
  await page.goto('/login');
  await page.getByTestId('login-identifier').fill(identifier);
  await page.getByTestId('login-password').fill(password);
  await page.getByTestId('login-submit').click();
}

// 断言当前上下文已经拿到有效登录态。
export async function expectAuthenticated(api: APIRequestContext): Promise<void> {
  const meResponse = await api.get('/api/auth/me');
  await expectStatus(meResponse, 200);
  const data = await readJson<{ success: boolean }>(meResponse);
  expect(data.success).toBe(true);
}
