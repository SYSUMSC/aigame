import type { APIRequestContext, APIResponse } from '@playwright/test';

// 比赛领域对象的最小创建与编辑载荷。
export interface CompetitionPayload {
  title: string;
  description: string;
  rules: string;
  startTime: string;
  endTime: string;
  bannerUrl?: string;
}

// 创建管理端比赛。
export async function createCompetition(api: APIRequestContext, payload: CompetitionPayload): Promise<APIResponse> {
  return api.post('/api/admin/competitions', {
    data: payload,
  });
}

// 更新管理端比赛。
export async function updateCompetition(api: APIRequestContext, competitionId: string, payload: CompetitionPayload & { solutionSubmissionDeadlineDays?: number }): Promise<APIResponse> {
  return api.put(`/api/admin/competitions/${competitionId}`, {
    data: payload,
  });
}

// 删除指定比赛。
export async function deleteCompetition(api: APIRequestContext, competitionId: string): Promise<APIResponse> {
  return api.delete(`/api/admin/competitions/${competitionId}`);
}

// 获取单个比赛详情。
export async function getCompetition(api: APIRequestContext, competitionId: string): Promise<APIResponse> {
  return api.get(`/api/admin/competitions/${competitionId}`);
}

// 统一封装比赛列表查询，方便覆盖筛选与分页断言。
export async function listAdminCompetitions(api: APIRequestContext, query?: Record<string, string | number>): Promise<APIResponse> {
  return api.get('/api/admin/competitions', { params: query });
}

// 创建队伍。
export async function createTeam(api: APIRequestContext, name: string): Promise<APIResponse> {
  return api.post('/api/teams', {
    data: { name },
  });
}

// 邀请成员加入队伍。
export async function inviteMember(api: APIRequestContext, teamId: string, email: string): Promise<APIResponse> {
  return api.post(`/api/teams/${teamId}/invite`, {
    data: { email },
  });
}

// 接受队伍邀请。
export async function acceptInvitation(api: APIRequestContext, invitationId: string): Promise<APIResponse> {
  return api.post(`/api/invitations/${invitationId}/accept`);
}

// 拒绝队伍邀请。
export async function rejectInvitation(api: APIRequestContext, invitationId: string): Promise<APIResponse> {
  return api.post(`/api/invitations/${invitationId}/reject`);
}

// 查询邀请详情。
export async function getInvitation(api: APIRequestContext, invitationId: string): Promise<APIResponse> {
  return api.get(`/api/invitations/${invitationId}`);
}

// 查询队伍详情。
export async function getTeam(api: APIRequestContext, teamId: string): Promise<APIResponse> {
  return api.get(`/api/teams/${teamId}`);
}

// 从队伍中移除指定成员。
export async function removeTeamMember(api: APIRequestContext, teamId: string, userId: string): Promise<APIResponse> {
  return api.delete(`/api/teams/${teamId}/remove`, {
    data: { userId },
  });
}

// 当前用户主动退出队伍。
export async function leaveTeam(api: APIRequestContext, teamId: string): Promise<APIResponse> {
  return api.post(`/api/teams/${teamId}/leave`);
}

// 让队伍报名参加比赛。
export async function joinCompetition(api: APIRequestContext, competitionId: string, teamId: string): Promise<APIResponse> {
  return api.post(`/api/competitions/${competitionId}/join`, {
    data: { teamId },
  });
}
