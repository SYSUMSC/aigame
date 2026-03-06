import bcrypt from 'bcryptjs';
import { MongoClient, ObjectId, type Db, type WithId, type Document } from 'mongodb';
import { readRuntimeState } from './runtime';

type UserDoc = WithId<Document> & {
  username: string;
  email: string;
  role: string;
  status: string;
  emailVerificationToken?: string | null;
  emailVerificationExpires?: Date | null;
  passwordResetToken?: string | null;
  passwordResetTokenExpiresAt?: Date | null;
};

let cachedClient: MongoClient | null = null;
let cachedDb: Db | null = null;

// 复用数据库连接，避免每个用例重复建立连接。
async function getDb(): Promise<Db> {
  if (cachedDb) {
    return cachedDb;
  }

  const runtime = await readRuntimeState();
  cachedClient = new MongoClient(runtime.mongoUri);
  await cachedClient.connect();
  cachedDb = cachedClient.db(runtime.mongoDbName);
  return cachedDb;
}

// 转义正则特殊字符，供按前缀清理测试数据时使用。
function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// 关闭缓存中的数据库连接。
export async function closeMongo(): Promise<void> {
  if (cachedClient) {
    await cachedClient.close();
  }
  cachedClient = null;
  cachedDb = null;
}

// 确保基线管理员账号存在，并具备可登录状态。
export async function ensureAdminUser(user: { username: string; email: string; password: string }): Promise<UserDoc> {
  const db = await getDb();
  const passwordHash = await bcrypt.hash(user.password, 12);
  const now = new Date();

  await db.collection<UserDoc>('users').updateOne(
    { $or: [{ username: user.username }, { email: user.email }] },
    {
      $set: {
        username: user.username,
        email: user.email,
        passwordHash,
        role: 'admin',
        status: 'ACTIVE',
        emailVerifiedAt: now,
        emailVerificationToken: null,
        emailVerificationExpires: null,
        passwordResetToken: null,
        passwordResetTokenExpiresAt: null,
        updatedAt: now,
      },
      $setOnInsert: {
        createdAt: now,
      },
    },
    { upsert: true },
  );

  const admin = await findUserByEmail(user.email);
  if (!admin) {
    throw new Error('无法创建或读取基线管理员账号');
  }

  return admin;
}

// 按邮箱查询用户，便于断言注册和密码找回状态。
export async function findUserByEmail(email: string): Promise<UserDoc | null> {
  const db = await getDb();
  return db.collection<UserDoc>('users').findOne({ email });
}

// 按用户名查询用户，便于核验界面与接口状态。
export async function findUserByUsername(username: string): Promise<UserDoc | null> {
  const db = await getDb();
  return db.collection<UserDoc>('users').findOne({ username });
}

// 统一更新用户字段，并自动刷新更新时间。
export async function updateUserByEmail(email: string, update: Record<string, unknown>): Promise<void> {
  const db = await getDb();
  await db.collection<UserDoc>('users').updateOne(
    { email },
    {
      $set: {
        ...update,
        updatedAt: new Date(),
      },
    },
  );
}

// 直接激活用户，绕过邮件验证流程。
export async function activateUser(email: string): Promise<void> {
  await updateUserByEmail(email, {
    status: 'ACTIVE',
    emailVerifiedAt: new Date(),
    emailVerificationToken: null,
    emailVerificationExpires: null,
  });
}

// 将用户标记为封禁状态。
export async function banUser(email: string): Promise<void> {
  await updateUserByEmail(email, {
    status: 'BANNED',
  });
}

// 写入邮箱验证令牌，便于覆盖验证成功与过期场景。
export async function setEmailVerification(
  email: string,
  token: string,
  expiresAt: Date,
  status: 'PENDING' | 'BANNED' = 'PENDING',
): Promise<void> {
  await updateUserByEmail(email, {
    status,
    emailVerificationToken: token,
    emailVerificationExpires: expiresAt,
    emailVerifiedAt: null,
  });
}

// 写入密码重置令牌，便于覆盖找回密码流程。
export async function setPasswordReset(email: string, token: string, expiresAt: Date): Promise<void> {
  await updateUserByEmail(email, {
    passwordResetToken: token,
    passwordResetTokenExpiresAt: expiresAt,
  });
}

// 按本轮运行前缀批量清理测试数据，避免污染下一轮执行。
export async function cleanupRunData(runId: string): Promise<void> {
  const db = await getDb();
  const prefix = `e2e_${runId}_`;
  const prefixRegex = new RegExp(`^${escapeRegExp(prefix)}`);
  const emailRegex = new RegExp(escapeRegExp(`${prefix}`));

  const users = await db.collection<UserDoc>('users').find({
    $or: [
      { username: prefixRegex },
      { email: emailRegex },
    ],
  }).toArray();

  const userIds = users.map((user) => user._id);

  if (userIds.length > 0) {
    await Promise.all([
      db.collection('users').deleteMany({ _id: { $in: userIds } }),
      db.collection('team_memberships').deleteMany({ userId: { $in: userIds.map((id) => id.toHexString()) } }),
      db.collection('submissions').deleteMany({ userId: { $in: userIds.map((id) => id.toHexString()) } }),
      db.collection('solutions').deleteMany({ userId: { $in: userIds.map((id) => id.toHexString()) } }),
      db.collection('invitations').deleteMany({
        $or: [
          { inviterId: { $in: userIds.map((id) => id.toHexString()) } },
          { inviteeId: { $in: userIds.map((id) => id.toHexString()) } },
        ],
      }),
    ]);
  }

  const teams = await db.collection('teams').find({ name: prefixRegex }).toArray();
  const teamIds = teams.map((team) => (team._id as ObjectId).toHexString());

  if (teamIds.length > 0) {
    await Promise.all([
      db.collection('team_memberships').deleteMany({ teamId: { $in: teamIds } }),
      db.collection('submissions').deleteMany({ teamId: { $in: teamIds } }),
      db.collection('solutions').deleteMany({ teamId: { $in: teamIds } }),
      db.collection('competition_cdks').deleteMany({ teamId: { $in: teamIds } }),
      db.collection('leaderboard_entries').deleteMany({ teamId: { $in: teamIds } }),
      db.collection('teams').deleteMany({ _id: { $in: teams.map((team) => team._id) } }),
    ]);
  }

  const competitions = await db.collection('competitions').find({ title: prefixRegex }).toArray();
  const competitionIds = competitions.map((competition) => (competition._id as ObjectId).toHexString());

  if (competitionIds.length > 0) {
    const problems = await db.collection('problems').find({ competitionId: { $in: competitionIds } }).toArray();
    const leaderboardIds = (await db.collection('leaderboards').find({ competitionId: { $in: competitionIds } }).toArray())
      .map((entry) => entry._id as ObjectId);

    await Promise.all([
      db.collection('problems').deleteMany({ competitionId: { $in: competitionIds } }),
      db.collection('submissions').deleteMany({ competitionId: { $in: competitionIds } }),
      db.collection('solutions').deleteMany({ competitionId: { $in: competitionIds } }),
      db.collection('competition_cdks').deleteMany({ competitionId: { $in: competitionIds } }),
      db.collection('problem_scores').deleteMany({ problemId: { $in: problems.map((problem) => (problem._id as ObjectId).toHexString()) } }),
      db.collection('leaderboard_entries').deleteMany({ leaderboardId: { $in: leaderboardIds.map((id) => id.toHexString()) } }),
      db.collection('leaderboards').deleteMany({ _id: { $in: leaderboardIds } }),
      db.collection('competitions').deleteMany({ _id: { $in: competitions.map((competition) => competition._id) } }),
    ]);
  }

  await Promise.all([
    db.collection('announcements').deleteMany({ title: prefixRegex }),
    db.collection('evaluate_nodes').deleteMany({ name: prefixRegex }),
  ]);
}


// 确保评测节点基线配置存在，并禁用其它旧节点，避免误命中历史脏数据。
export async function ensureEvaluateNode(node: {
  name: string;
  baseUrl: string;
  sharedSecret: string;
  callbackUrl?: string;
}): Promise<void> {
  const db = await getDb();
  const now = new Date();

  await db.collection('evaluate_nodes').updateMany(
    { name: { $ne: node.name } },
    {
      $set: {
        active: false,
        updatedAt: now,
      },
    },
  );

  await db.collection('evaluate_nodes').updateOne(
    { name: node.name },
    {
      $set: {
        name: node.name,
        baseUrl: node.baseUrl,
        sharedSecret: node.sharedSecret,
        callbackUrl: node.callbackUrl ?? null,
        active: true,
        updatedAt: now,
      },
      $setOnInsert: {
        createdAt: now,
      },
    },
    { upsert: true },
  );
}
