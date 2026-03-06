import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const e2eRoot = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const stateDir = path.join(e2eRoot, '.state');
const runtimeFile = path.join(stateDir, 'runtime.json');

export interface RuntimeState {
  runId: string;
  baseURL: string;
  evaluateBaseURL: string;
  mongoUri: string;
  mongoDbName: string;
  admin: {
    username: string;
    email: string;
    password: string;
  };
  files: {
    judgeZip: string;
    submissionZip: string;
  };
}

// 返回端到端测试工程根目录，供脚本定位相对路径。
export function getE2ERoot(): string {
  return e2eRoot;
}

// 返回主仓库根目录，便于拼装样例文件路径。
export function getRepoRoot(): string {
  return path.resolve(e2eRoot, '..');
}

// 暴露运行态文件路径，便于调试与排障。
export function getRuntimeFilePath(): string {
  return runtimeFile;
}

// 将本轮测试上下文持久化到磁盘，供不同进程共享。
export async function writeRuntimeState(state: RuntimeState): Promise<void> {
  await fs.mkdir(stateDir, { recursive: true });
  await fs.writeFile(runtimeFile, JSON.stringify(state, null, 2), 'utf8');
}

// 读取全局初始化生成的运行态配置。
export async function readRuntimeState(): Promise<RuntimeState> {
  const raw = await fs.readFile(runtimeFile, 'utf8');
  return JSON.parse(raw) as RuntimeState;
}

// 清理运行态文件，避免后续误读旧上下文。
export async function removeRuntimeState(): Promise<void> {
  await fs.rm(runtimeFile, { force: true });
}
