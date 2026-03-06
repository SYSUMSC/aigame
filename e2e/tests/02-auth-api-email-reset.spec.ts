import { expect, test } from '@playwright/test';
import { createApiContext, expectStatus } from '../utils/apiClient';
import { loginUser, registerUser } from '../utils/auth';
import { createTestUser } from '../utils/factory';
import { activateUser, banUser, findUserByEmail, setEmailVerification, setPasswordReset } from '../utils/mongo';

test.describe('02-认证接口与找回密码', () => {
  test('邮箱验证接口使用数据库中的令牌可以成功激活', async () => {
    const api = await createApiContext();
    const user = await createTestUser('verify-email-success');

    await expectStatus(await registerUser(api, user), 200);
    const dbUser = await findUserByEmail(user.email);
    expect(dbUser?.emailVerificationToken).toBeTruthy();

    const response = await api.post('/api/auth/verify-email', {
      data: {
        email: user.email,
        token: dbUser?.emailVerificationToken,
      },
    });

    await expectStatus(response, 200);
    const refreshedUser = await findUserByEmail(user.email);
    expect(refreshedUser?.status).toBe('ACTIVE');
    await api.dispose();
  });

  test('邮箱验证接口会拒绝无效和过期令牌', async () => {
    const api = await createApiContext();

    const invalidUser = await createTestUser('verify-email-invalid');
    await expectStatus(await registerUser(api, invalidUser), 200);
    const invalidResponse = await api.post('/api/auth/verify-email', {
      data: {
        email: invalidUser.email,
        token: 'bad-token',
      },
    });
    await expectStatus(invalidResponse, 400);

    const expiredUser = await createTestUser('verify-email-expired');
    await expectStatus(await registerUser(api, expiredUser), 200);
    await setEmailVerification(expiredUser.email, 'expired-token', new Date(Date.now() - 60_000));

    const expiredResponse = await api.post('/api/auth/verify-email', {
      data: {
        email: expiredUser.email,
        token: 'expired-token',
      },
    });
    await expectStatus(expiredResponse, 400);

    await api.dispose();
  });

  test('待激活用户重发验证邮件时会刷新令牌', async () => {
    const api = await createApiContext();
    const user = await createTestUser('resend-verification');

    await expectStatus(await registerUser(api, user), 200);
    const before = await findUserByEmail(user.email);

    const response = await api.post('/api/auth/resend-verification', {
      data: { email: user.email },
    });

    await expectStatus(response, 200);
    const after = await findUserByEmail(user.email);
    expect(after?.emailVerificationToken).toBeTruthy();
    expect(after?.emailVerificationToken).not.toBe(before?.emailVerificationToken);
    await api.dispose();
  });

  test('忘记密码与重置密码覆盖成功和异常状态', async () => {
    const api = await createApiContext();

    const activeUser = await createTestUser('forgot-success');
    await expectStatus(await registerUser(api, activeUser), 200);
    await activateUser(activeUser.email);

    const forgotResponse = await api.post('/api/auth/forgot-password', {
      data: { email: activeUser.email },
    });
    await expectStatus(forgotResponse, 200);

    const afterForgot = await findUserByEmail(activeUser.email);
    expect(afterForgot?.passwordResetToken).toBeTruthy();

    const invalidResetResponse = await api.post('/api/auth/reset-password', {
      data: {
        email: activeUser.email,
        token: 'invalid-token',
        newPassword: 'NewPassw0rd!'
      },
    });
    await expectStatus(invalidResetResponse, 400);

    await setPasswordReset(activeUser.email, 'expired-reset-token', new Date(Date.now() - 60_000));
    const expiredResetResponse = await api.post('/api/auth/reset-password', {
      data: {
        email: activeUser.email,
        token: 'expired-reset-token',
        newPassword: 'NewPassw0rd!'
      },
    });
    await expectStatus(expiredResetResponse, 400);

    const finalToken = 'final-reset-token';
    await setPasswordReset(activeUser.email, finalToken, new Date(Date.now() + 60 * 60 * 1000));
    const successResetResponse = await api.post('/api/auth/reset-password', {
      data: {
        email: activeUser.email,
        token: finalToken,
        newPassword: 'NewPassw0rd!'
      },
    });
    await expectStatus(successResetResponse, 200);

    const reloginApi = await createApiContext();
    const reloginResponse = await loginUser(reloginApi, activeUser.email, 'NewPassw0rd!');
    await expectStatus(reloginResponse, 200);
    await reloginApi.dispose();

    const pendingUser = await createTestUser('forgot-pending');
    await expectStatus(await registerUser(api, pendingUser), 200);
    const pendingForgotResponse = await api.post('/api/auth/forgot-password', {
      data: { email: pendingUser.email },
    });
    await expectStatus(pendingForgotResponse, 403);

    const bannedUser = await createTestUser('verify-banned');
    await expectStatus(await registerUser(api, bannedUser), 200);
    await banUser(bannedUser.email);
    await setEmailVerification(bannedUser.email, 'banned-token', new Date(Date.now() + 60_000), 'BANNED');
    const bannedVerifyResponse = await api.post('/api/auth/verify-email', {
      data: { email: bannedUser.email, token: 'banned-token' },
    });
    await expectStatus(bannedVerifyResponse, 403);

    await api.dispose();
  });
});
