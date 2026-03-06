import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import type { APIRequestContext, APIResponse } from '@playwright/test';

export interface SubmissionCallbackPayload {
  submissionId: string;
  status: 'COMPLETED' | 'ERROR';
  score: number;
  logs?: string;
}

function canonicalize(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalize(item)).join(',')}]`;
  }

  const entries = Object.entries(value as Record<string, unknown>).sort(([left], [right]) => left.localeCompare(right));
  return `{${entries.map(([key, item]) => `${JSON.stringify(key)}:${canonicalize(item)}`).join(',')}}`;
}

function buildCallbackHeaders(payload: SubmissionCallbackPayload, secret: string) {
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const contentHash = crypto.createHash('sha256').update(canonicalize(payload)).digest('hex');
  const sign = crypto.createHmac('sha256', secret).update(`${timestamp}\n${contentHash}`).digest('hex');

  return {
    'x-timestamp': timestamp,
    'x-content-hash': contentHash,
    'x-sign': sign,
  };
}

// 上传参赛提交压缩包。
export async function uploadSubmission(
  api: APIRequestContext,
  params: { problemId: string; competitionId: string; teamId: string; filePath: string },
): Promise<APIResponse> {
  return api.post('/api/submissions/upload', {
    multipart: {
      problemId: params.problemId,
      competitionId: params.competitionId,
      teamId: params.teamId,
      file: {
        name: path.basename(params.filePath),
        mimeType: 'application/zip',
        buffer: await fs.readFile(params.filePath),
      },
    },
  });
}

// 查询单个提交详情。
export async function getSubmission(api: APIRequestContext, submissionId: string): Promise<APIResponse> {
  return api.get(`/api/submissions/${submissionId}`);
}

// 查询当前用户可见的提交列表。
export async function listSubmissions(api: APIRequestContext, query?: Record<string, string | number>): Promise<APIResponse> {
  return api.get('/api/submissions', {
    params: query,
  });
}

// 查询管理端提交列表。
export async function listAdminSubmissions(api: APIRequestContext, query?: Record<string, string | number>): Promise<APIResponse> {
  return api.get('/api/admin/submissions', {
    params: query,
  });
}

// 重新入队某条提交。
export async function requeueSubmission(api: APIRequestContext, submissionId: string): Promise<APIResponse> {
  return api.post(`/api/admin/submissions/${submissionId}/requeue`);
}

// 查询比赛排行榜。
export async function getCompetitionLeaderboard(api: APIRequestContext, competitionId: string): Promise<APIResponse> {
  return api.get(`/api/competitions/${competitionId}/leaderboard`);
}

// 发送带合法签名的评测回调。
export async function sendSignedSubmissionCallback(
  api: APIRequestContext,
  payload: SubmissionCallbackPayload,
  secret = process.env.E2E_SHARED_SECRET || 'aigame-e2e-shared-secret',
): Promise<APIResponse> {
  return api.post('/api/submissions/callback', {
    data: payload,
    headers: buildCallbackHeaders(payload, secret),
  });
}

// 发送带错误签名的评测回调，用于覆盖鉴权失败场景。
export async function sendInvalidSubmissionCallback(api: APIRequestContext, payload: SubmissionCallbackPayload): Promise<APIResponse> {
  return sendSignedSubmissionCallback(api, payload, 'wrong-secret-for-e2e');
}
