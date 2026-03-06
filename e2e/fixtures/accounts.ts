// 基线管理员账号，供全局初始化与管理端测试复用。
export const adminAccount = {
  username: 'admin',
  email: 'admin@example.com',
  password: '123456',
} as const;

// 测试普通用户默认密码。
export const defaultUserPassword = 'Passw0rd!';
