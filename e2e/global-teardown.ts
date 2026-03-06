import { cleanupRunData, closeMongo } from './utils/mongo';
import { readRuntimeState, removeRuntimeState } from './utils/runtime';

export default async function globalTeardown(): Promise<void> {
  try {
    // 优先清理本轮运行标识产生的数据，避免污染下一次执行。
    const runtime = await readRuntimeState();
    await cleanupRunData(runtime.runId);
  } finally {
    // 无论测试是否成功，都要关闭连接并删除运行态文件。
    await closeMongo();
    await removeRuntimeState();
  }
}
