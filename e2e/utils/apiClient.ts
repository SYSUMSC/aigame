import { expect, request, type APIRequestContext, type APIResponse } from '@playwright/test';
import { readRuntimeState } from './runtime';

// 创建共享运行态中的接口请求上下文。
export async function createApiContext(): Promise<APIRequestContext> {
  const runtime = await readRuntimeState();
  return request.newContext({
    baseURL: runtime.baseURL,
    ignoreHTTPSErrors: true,
  });
}

// 读取结构化响应体并保留调用方声明的类型。
export async function readJson<T>(response: APIResponse): Promise<T> {
  return response.json() as Promise<T>;
}

// 尽量从响应体中提取更友好的错误信息。
export async function readErrorMessage(response: APIResponse): Promise<string> {
  try {
    const body = await response.json();
    return body.statusMessage || body.message || JSON.stringify(body);
  } catch {
    return response.statusText();
  }
}

// 断言接口状态码，并在失败时输出服务端错误详情。
export async function expectStatus(response: APIResponse, status: number): Promise<void> {
  const message = await readErrorMessage(response);
  expect(response.status(), message).toBe(status);
}
