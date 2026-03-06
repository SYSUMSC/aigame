import { expect, test } from '@playwright/test';
import { createApiContext, expectStatus, readJson } from '../utils/apiClient';
import { createAdminApiContext, createRegisteredUserApiContext } from '../utils/auth';
import { createCompetition, createTeam, joinCompetition, type CompetitionPayload } from '../utils/domain';
import { sampleFiles } from '../fixtures/files';
import { createTestUser } from '../utils/factory';
import { createProblem, listCompetitionProblems, uploadProblemSample, uploadProblemScript } from '../utils/problem';
import { pollUntil } from '../utils/polling';
import { getCompetitionLeaderboard, getSubmission, listAdminSubmissions, requeueSubmission, sendInvalidSubmissionCallback, sendSignedSubmissionCallback, uploadSubmission } from '../utils/submission';
import { readRuntimeState } from '../utils/runtime';

function buildCompetitionPayload(title: string, startOffsetMinutes: number, endOffsetMinutes: number): CompetitionPayload {
  const now = Date.now();
  return {
    title,
    description: `${title} description`,
    rules: `${title} rules`,
    startTime: new Date(now + startOffsetMinutes * 60_000).toISOString(),
    endTime: new Date(now + endOffsetMinutes * 60_000).toISOString(),
  };
}

test.describe('08-提交与评测', () => {
  test('提交上传、状态流转、回调鉴权、重新入队与排行榜保高分都能覆盖', async () => {
    test.setTimeout(180_000);

    const adminApi = await createAdminApiContext();
    const publicApi = await createApiContext();
    const { runId, files } = await readRuntimeState();
    const prefix = `e2e_${runId}_submission`;

    const captain = await createTestUser('submission-captain');
    const captainApi = await createRegisteredUserApiContext(captain, { activate: true });

    try {
      const competitionResponse = await createCompetition(adminApi, buildCompetitionPayload(`${prefix}_competition`, -60, 360));
      await expectStatus(competitionResponse, 200);
      const competition = await readJson<{ competition: { id: string; startTime: string; endTime: string } }>(competitionResponse);

      const scriptUploadResponse = await uploadProblemScript(adminApi, files.judgeZip);
      const sampleUploadResponse = await uploadProblemSample(adminApi, files.submissionZip);
      await expectStatus(scriptUploadResponse, 200);
      await expectStatus(sampleUploadResponse, 200);
      const scriptUpload = await readJson<{ url: string }>(scriptUploadResponse);
      const sampleUpload = await readJson<{ url: string }>(sampleUploadResponse);

      const problemResponse = await createProblem(adminApi, competition.competition.id, {
        title: `${prefix}_problem`,
        shortDescription: '提交流程题目',
        detailedDescription: '用于覆盖提交流程与评测回调。',
        judgingScriptUrl: scriptUpload.url,
        sampleSubmissionUrl: sampleUpload.url,
        startTime: new Date(new Date(competition.competition.startTime).getTime() + 10 * 60_000).toISOString(),
        endTime: new Date(new Date(competition.competition.endTime).getTime() - 10 * 60_000).toISOString(),
        score: 100,
      });
      await expectStatus(problemResponse, 200);
      const problem = await readJson<{ problem: { id: string } }>(problemResponse);

      const teamResponse = await createTeam(captainApi, `${prefix}_team`);
      await expectStatus(teamResponse, 200);
      const team = await readJson<{ team: { id: string } }>(teamResponse);

      const joinResponse = await joinCompetition(captainApi, competition.competition.id, team.team.id);
      await expectStatus(joinResponse, 200);

      const invalidSubmissionResponse = await captainApi.post('/api/submissions/upload', {
        multipart: {
          problemId: problem.problem.id,
          competitionId: competition.competition.id,
          teamId: team.team.id,
          file: {
            name: 'not-zip.txt',
            mimeType: 'text/plain',
            buffer: Buffer.from('this is not a zip file', 'utf8'),
          },
        },
      });
      await expectStatus(invalidSubmissionResponse, 400);

      const queuedSubmissionResponse = await uploadSubmission(captainApi, {
        problemId: problem.problem.id,
        competitionId: competition.competition.id,
        teamId: team.team.id,
        filePath: files.submissionZip,
      });
      await expectStatus(queuedSubmissionResponse, 200);
      const queuedSubmission = await readJson<{ submission: { id: string; status: string } }>(queuedSubmissionResponse);
      expect(queuedSubmission.submission.status).toBe('QUEUED');

      const seenStatuses = new Set<string>(['QUEUED']);
      const firstMovedSubmission = await pollUntil(
        async () => {
          const response = await getSubmission(captainApi, queuedSubmission.submission.id);
          await expectStatus(response, 200);
          const body = await readJson<{ submission: { status: string } }>(response);
          seenStatuses.add(body.submission.status);
          return body.submission;
        },
        (submission) => submission.status !== 'QUEUED',
        {
          timeoutMs: 30_000,
          intervalMs: 1_000,
          description: '等待提交离开排队状态',
        },
      );
      expect(['JUDGING', 'COMPLETED', 'ERROR']).toContain(firstMovedSubmission.status);

      const finalSubmission = await pollUntil(
        async () => {
          const response = await getSubmission(captainApi, queuedSubmission.submission.id);
          await expectStatus(response, 200);
          const body = await readJson<{
            submission: {
              id: string;
              status: string;
              score: number | null;
              executionLogs: string | null;
            };
          }>(response);
          seenStatuses.add(body.submission.status);
          return body.submission;
        },
        (submission) => submission.status === 'COMPLETED' || submission.status === 'ERROR',
        {
          timeoutMs: 120_000,
          intervalMs: 1_500,
          description: '等待提交评测完成',
        },
      );
      expect(finalSubmission.status).toBe('COMPLETED');
      expect(finalSubmission.score).toBe(52.5);
      expect(finalSubmission.executionLogs).toContain('最终总和为 52.5');
      expect(seenStatuses.has('QUEUED')).toBe(true);
      expect(seenStatuses.has('COMPLETED')).toBe(true);

      const adminSubmissionsResponse = await listAdminSubmissions(adminApi, { id: queuedSubmission.submission.id });
      await expectStatus(adminSubmissionsResponse, 200);
      const adminSubmissions = await readJson<{ submissions: Array<{ id: string; status: string }> }>(adminSubmissionsResponse);
      expect(adminSubmissions.submissions.some((submission) => submission.id === queuedSubmission.submission.id)).toBe(true);

      const competitionProblemsResponse = await listCompetitionProblems(captainApi, competition.competition.id, { limit: 20 });
      await expectStatus(competitionProblemsResponse, 200);
      const competitionProblems = await readJson<{ problems: Array<{ id: string; userBestScore: number }> }>(competitionProblemsResponse);
      expect(competitionProblems.problems.find((entry) => entry.id === problem.problem.id)?.userBestScore).toBe(52.5);

      const leaderboardBeforeResponse = await getCompetitionLeaderboard(publicApi, competition.competition.id);
      await expectStatus(leaderboardBeforeResponse, 200);
      const leaderboardBefore = await readJson<{
        leaderboard: Array<{
          team: { id: string };
          totalScore: number;
          problemScores: Array<{ problemId: string; score: number }>;
        }>;
      }>(leaderboardBeforeResponse);
      const teamBefore = leaderboardBefore.leaderboard.find((entry) => entry.team.id === team.team.id);
      expect(teamBefore?.totalScore).toBe(52.5);
      expect(teamBefore?.problemScores.find((item) => item.problemId === problem.problem.id)?.score).toBe(52.5);

      const invalidCallbackResponse = await sendInvalidSubmissionCallback(publicApi, {
        submissionId: queuedSubmission.submission.id,
        status: 'COMPLETED',
        score: 1,
        logs: '错误签名回调',
      });
      await expectStatus(invalidCallbackResponse, 401);

      const requeueResponse = await requeueSubmission(adminApi, queuedSubmission.submission.id);
      await expectStatus(requeueResponse, 200);

      const requeueStatuses = new Set<string>();
      const finalRequeuedSubmission = await pollUntil(
        async () => {
          const response = await getSubmission(captainApi, queuedSubmission.submission.id);
          await expectStatus(response, 200);
          const body = await readJson<{ submission: { status: string; score: number | null } }>(response);
          requeueStatuses.add(body.submission.status);
          return body.submission;
        },
        (submission) => submission.status === 'COMPLETED' || submission.status === 'ERROR',
        {
          timeoutMs: 120_000,
          intervalMs: 1_500,
          description: '等待重新入队后的评测完成',
        },
      );
      expect(requeueStatuses.has('PENDING') || requeueStatuses.has('JUDGING') || requeueStatuses.has('COMPLETED')).toBe(true);
      expect(finalRequeuedSubmission.status).toBe('COMPLETED');
      expect(finalRequeuedSubmission.score).toBe(52.5);

      const lowerScoreCallbackResponse = await sendSignedSubmissionCallback(publicApi, {
        submissionId: queuedSubmission.submission.id,
        status: 'COMPLETED',
        score: 1,
        logs: '人工回调，将得分降到 1 分',
      });
      await expectStatus(lowerScoreCallbackResponse, 200);

      const loweredSubmissionResponse = await getSubmission(captainApi, queuedSubmission.submission.id);
      await expectStatus(loweredSubmissionResponse, 200);
      const loweredSubmission = await readJson<{ submission: { score: number | null; status: string } }>(loweredSubmissionResponse);
      expect(loweredSubmission.submission.status).toBe('COMPLETED');
      expect(loweredSubmission.submission.score).toBe(1);

      const leaderboardAfterResponse = await getCompetitionLeaderboard(publicApi, competition.competition.id);
      await expectStatus(leaderboardAfterResponse, 200);
      const leaderboardAfter = await readJson<{
        leaderboard: Array<{
          team: { id: string };
          totalScore: number;
          problemScores: Array<{ problemId: string; score: number }>;
        }>;
      }>(leaderboardAfterResponse);
      const teamAfter = leaderboardAfter.leaderboard.find((entry) => entry.team.id === team.team.id);
      expect(teamAfter?.totalScore).toBe(52.5);
      expect(teamAfter?.problemScores.find((item) => item.problemId === problem.problem.id)?.score).toBe(52.5);

      const competitionProblemsAfterResponse = await listCompetitionProblems(captainApi, competition.competition.id, { limit: 20 });
      await expectStatus(competitionProblemsAfterResponse, 200);
      const competitionProblemsAfter = await readJson<{ problems: Array<{ id: string; userBestScore: number }> }>(competitionProblemsAfterResponse);
      expect(competitionProblemsAfter.problems.find((entry) => entry.id === problem.problem.id)?.userBestScore).toBe(52.5);
    } finally {
      await Promise.all([
        adminApi.dispose(),
        publicApi.dispose(),
        captainApi.dispose(),
      ]);
    }
  });
});
