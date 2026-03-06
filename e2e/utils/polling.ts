// 简单休眠工具，用于轮询间隔控制。
export async function sleep(ms: number): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

// 轮询某个异步操作，直到满足条件或超时。
export async function pollUntil<T>(
  operation: () => Promise<T>,
  predicate: (value: T) => boolean,
  options: {
    timeoutMs?: number;
    intervalMs?: number;
    description?: string;
  } = {},
): Promise<T> {
  const timeoutMs = options.timeoutMs ?? 30_000;
  const intervalMs = options.intervalMs ?? 1_000;
  const startedAt = Date.now();

  // 持续轮询直到命中条件或触发超时。
  while (true) {
    const value = await operation();
    if (predicate(value)) {
      return value;
    }

    if (Date.now() - startedAt >= timeoutMs) {
      throw new Error(options.description || `轮询在 ${timeoutMs}ms 后超时`);
    }

    await sleep(intervalMs);
  }
}

// 等待接口返回预期状态码，用于启动阶段健康检查。
export async function waitForHttp(
  url: string,
  options: {
    timeoutMs?: number;
    intervalMs?: number;
    expectedStatuses?: number[];
  } = {},
): Promise<void> {
  const expectedStatuses = options.expectedStatuses ?? [200];

  await pollUntil(
    async () => {
      try {
        const response = await fetch(url);
        return response.status;
      } catch {
        return 0;
      }
    },
    (status) => expectedStatuses.includes(status),
    {
      timeoutMs: options.timeoutMs ?? 180_000,
      intervalMs: options.intervalMs ?? 2_000,
      description: `等待 ${url} 返回以下状态码之一：${expectedStatuses.join(', ')}`,
    },
  );
}
