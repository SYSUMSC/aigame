import fs from 'node:fs/promises';
import path from 'node:path';
import type { APIRequestContext, APIResponse } from '@playwright/test';

export interface ProblemPayload {
  title: string;
  shortDescription: string;
  detailedDescription: string;
  startTime: string;
  endTime: string;
  score?: number;
  datasetUrl?: string;
  judgingScriptUrl?: string;
  sampleSubmissionUrl?: string;
}

async function buildZipMultipart(filePath: string) {
  return {
    name: path.basename(filePath),
    mimeType: 'application/zip',
    buffer: await fs.readFile(filePath),
  };
}

// 上传题目数据集压缩包。
export async function uploadProblemDataset(api: APIRequestContext, filePath: string): Promise<APIResponse> {
  return api.post('/api/admin/problems/dataset/upload', {
    multipart: {
      dataset: await buildZipMultipart(filePath),
    },
  });
}

// 上传题目评测脚本压缩包。
export async function uploadProblemScript(api: APIRequestContext, filePath: string): Promise<APIResponse> {
  return api.post('/api/admin/problems/script/upload', {
    multipart: {
      script: await buildZipMultipart(filePath),
    },
  });
}

// 上传题目样例提交压缩包。
export async function uploadProblemSample(api: APIRequestContext, filePath: string): Promise<APIResponse> {
  return api.post('/api/admin/problems/sample/upload', {
    multipart: {
      sample: await buildZipMultipart(filePath),
    },
  });
}

// 在指定比赛下创建单个题目。
export async function createProblem(api: APIRequestContext, competitionId: string, payload: ProblemPayload): Promise<APIResponse> {
  return api.post(`/api/admin/competitions/${competitionId}/problems`, {
    data: payload,
  });
}

// 更新单个题目。
export async function updateProblem(api: APIRequestContext, problemId: string, payload: ProblemPayload): Promise<APIResponse> {
  return api.put(`/api/admin/problems/${problemId}`, {
    data: payload,
  });
}

// 删除单个题目。
export async function deleteProblem(api: APIRequestContext, problemId: string): Promise<APIResponse> {
  return api.delete(`/api/admin/problems/${problemId}`);
}

// 查询管理端题目列表。
export async function listAdminProblems(api: APIRequestContext, query?: Record<string, string | number>): Promise<APIResponse> {
  return api.get('/api/admin/problems', {
    params: query,
  });
}

// 查询公开题目详情。
export async function getProblemDetail(api: APIRequestContext, problemId: string): Promise<APIResponse> {
  return api.get(`/api/problems/${problemId}`);
}

// 批量上传题目包，单次传入一个压缩文件。
export async function batchUploadProblems(
  api: APIRequestContext,
  competitionId: string,
  mode: 'create' | 'overwrite',
  filePath: string,
): Promise<APIResponse> {
  return api.post('/api/admin/problems/upload', {
    multipart: {
      competitionId,
      mode,
      files: await buildZipMultipart(filePath),
    },
  });
}

// 查询比赛下的公开题目列表。
export async function listCompetitionProblems(api: APIRequestContext, competitionId: string, query?: Record<string, string | number>): Promise<APIResponse> {
  return api.get(`/api/competitions/${competitionId}/problems`, {
    params: query,
  });
}
