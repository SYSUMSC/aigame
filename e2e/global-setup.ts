import fs from 'node:fs';
import { adminAccount } from './fixtures/accounts';
import { sampleFiles } from './fixtures/files';
import { ensureAdminUser, ensureEvaluateNode } from './utils/mongo';
import { waitForHttp } from './utils/polling';
import { writeRuntimeState } from './utils/runtime';

// 为每轮运行生成独立运行标识，便于隔离测试数据。
function buildRunId(): string {
  const candidate = process.env.CI_RUN_ID || `${Date.now()}`;
  return candidate.replace(/[^a-zA-Z0-9_-]/g, '-');
}

export default async function globalSetup(): Promise<void> {
  const runId = buildRunId();
  const baseURL = process.env.E2E_BASE_URL || `http://127.0.0.1:${process.env.WEBAPP_HOST_PORT || '33000'}`;
  const evaluateBaseURL = process.env.E2E_EVALUATE_BASE_URL || `http://127.0.0.1:${process.env.EVALUATEAPP_HOST_PORT || '38000'}`;
  const mongoUri = process.env.E2E_MONGODB_URI || `mongodb://root:password@127.0.0.1:${process.env.MONGO_HOST_PORT || '37017'}/aigame?authSource=admin&replicaSet=rs0&directConnection=true`;
  const evaluateNodeBaseUrl = process.env.E2E_INTERNAL_EVALUATE_BASE_URL || 'http://evaluateapp:8000';
  const evaluateNodeCallbackBaseUrl = process.env.E2E_INTERNAL_WEBAPP_BASE_URL || 'http://webapp:3000';
  const evaluateNodeSharedSecret = process.env.E2E_SHARED_SECRET || 'aigame-e2e-shared-secret';

  // 启动前先确认样例文件存在，避免后续评测链路在运行时才失败。
  for (const file of Object.values(sampleFiles)) {
    if (!fs.existsSync(String(file))) {
      throw new Error(`Missing fixture file: ${String(file)}`);
    }
  }

  // 将本轮运行需要的上下文写入状态文件，供各个测试文件共享读取。
  await writeRuntimeState({
    runId,
    baseURL,
    evaluateBaseURL,
    mongoUri,
    mongoDbName: process.env.E2E_MONGODB_DB || 'aigame',
    admin: adminAccount,
    files: sampleFiles,
  });

  // 等待核心服务可用，并确保基线管理员账户存在。
  await waitForHttp(`${baseURL}/api/settings`);
  await waitForHttp(`${evaluateBaseURL}/openapi.json`);
  await ensureAdminUser(adminAccount);
  await ensureEvaluateNode({
    name: 'node-1',
    baseUrl: evaluateNodeBaseUrl,
    sharedSecret: evaluateNodeSharedSecret,
    callbackUrl: evaluateNodeCallbackBaseUrl,
  });
}
