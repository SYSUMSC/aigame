import { randomUUID } from 'node:crypto';
import { defaultUserPassword } from '../fixtures/accounts';
import { readRuntimeState } from './runtime';

export interface TestUser {
  username: string;
  email: string;
  password: string;
  realName: string;
  studentId: string;
  phoneNumber: string;
  education: 'BACHELOR' | 'MASTER' | 'DOCTORATE';
}

// 从随机种子中提取数字，稳定生成学号和手机号尾号。
function buildNumericSuffix(seed: string, length: number): string {
  const digits = seed.replace(/\D/g, '');
  return (digits + '1234567890123456').slice(0, length);
}

// 为当前测试运行生成互不冲突的用户数据。
export async function createTestUser(tag: string, overrides: Partial<TestUser> = {}): Promise<TestUser> {
  const { runId } = await readRuntimeState();
  const suffix = randomUUID().replace(/-/g, '').slice(0, 8);
  const base = `e2e_${runId}_${tag}_${suffix}`.toLowerCase();

  return {
    username: overrides.username ?? base,
    email: overrides.email ?? `${base}@example.com`,
    password: overrides.password ?? defaultUserPassword,
    realName: overrides.realName ?? 'E2E 测试用户',
    studentId: overrides.studentId ?? `2026${buildNumericSuffix(suffix, 8)}`,
    phoneNumber: overrides.phoneNumber ?? `138${buildNumericSuffix(suffix, 8)}`,
    education: overrides.education ?? 'BACHELOR',
  };
}
