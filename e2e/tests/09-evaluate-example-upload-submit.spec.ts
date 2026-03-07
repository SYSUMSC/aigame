import { expect, test } from '@playwright/test';
import { expectStatus, readJson } from '../utils/apiClient';
import { createAdminApiContext, createRegisteredUserApiContext } from '../utils/auth';
import { createCompetition, createTeam, joinCompetition, type CompetitionPayload } from '../utils/domain';
import { sampleFiles } from '../fixtures/files';
import { createTestUser } from '../utils/factory';
import { listCompetitionProblems, batchUploadProblems, getProblemDetail } from '../utils/problem';
import { pollUntil } from '../utils/polling';
import { buildPackagedProblemFromExample, type BuiltPackagedExampleArchive } from '../utils/problemPackage';
import { getSubmission, uploadSubmission } from '../utils/submission';
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

test.describe('09-样例题目上传与示例提交', () => {
  test('管理员上传 evaluate_example 题目包后，普通用户可以提交 test_submit.zip 并完成评测', async () => {
    test.setTimeout(180_000);

    const adminApi = await createAdminApiContext();
    const { runId } = await readRuntimeState();
    const prefix = `e2e_${runId}_example_retry${test.info().retry}`;

    const participant = await createTestUser('evaluate-example-player');
    const participantApi = await createRegisteredUserApiContext(participant, { activate: true });
    let packagedProblem: BuiltPackagedExampleArchive | null = null;

    try {
      const competitionResponse = await createCompetition(adminApi, buildCompetitionPayload(`${prefix}_competition`, -60, 360));
      await expectStatus(competitionResponse, 200);
      const competition = await readJson<{ competition: { id: string } }>(competitionResponse);

      packagedProblem = await buildPackagedProblemFromExample(sampleFiles.judgeSumDir, {
        archiveName: `${prefix}_judge_sum_package`,
        taskDirName: `${prefix}_judge_sum_dir`,
        title: `${prefix}_judge_sum`,
        shortDescription: '基于 evaluate_example/judge_sum 打包上传',
        detailedDescription: 'E2E staging 包：来自 evaluate_example/judge_sum，用于验证题目上传后他人可直接提交 test_submit.zip。',
        startTime: new Date(Date.now() - 20 * 60_000).toISOString(),
        endTime: new Date(Date.now() + 200 * 60_000).toISOString(),
        score: 1000,
      });

      const uploadResponse = await batchUploadProblems(adminApi, competition.competition.id, 'create', packagedProblem.archivePath);
      await expectStatus(uploadResponse, 200);
      const uploadResult = await readJson<{ results: Array<{ problemId: string; title: string; mode: string }> }>(uploadResponse);
      expect(uploadResult.results).toHaveLength(1);
      expect(uploadResult.results[0]?.mode).toBe('created');
      expect(uploadResult.results[0]?.title).toBe(`${prefix}_judge_sum`);
      const uploadedProblemId = uploadResult.results[0]!.problemId;

      const adminProblemResponse = await getProblemDetail(adminApi, uploadedProblemId);
      await expectStatus(adminProblemResponse, 200);
      const adminProblem = await readJson<{
        problem: {
          id: string;
          title: string;
          datasetUrl: string | null;
          sampleSubmissionUrl: string | null;
          detailedDescription: string;
        };
      }>(adminProblemResponse);
      expect(adminProblem.problem.id).toBe(uploadedProblemId);
      expect(adminProblem.problem.title).toBe(`${prefix}_judge_sum`);
      expect(adminProblem.problem.datasetUrl).toBeNull();
      expect(adminProblem.problem.sampleSubmissionUrl).toContain('/aigame/problems/samples/');
      expect(adminProblem.problem.detailedDescription).toContain('evaluate_example/judge_sum');

      const teamResponse = await createTeam(participantApi, `${prefix}_team`);
      await expectStatus(teamResponse, 200);
      const team = await readJson<{ team: { id: string } }>(teamResponse);

      const joinResponse = await joinCompetition(participantApi, competition.competition.id, team.team.id);
      await expectStatus(joinResponse, 200);

      const problemsBeforeResponse = await listCompetitionProblems(participantApi, competition.competition.id, { limit: 20 });
      await expectStatus(problemsBeforeResponse, 200);
      const problemsBefore = await readJson<{
        problems: Array<{ id: string; title: string; status: string; userBestScore: number }>;
      }>(problemsBeforeResponse);
      const uploadedProblem = problemsBefore.problems.find((problem) => problem.id === uploadedProblemId);
      expect(uploadedProblem?.title).toBe(`${prefix}_judge_sum`);
      expect(uploadedProblem?.status).toBe('ongoing');
      expect(uploadedProblem?.userBestScore).toBe(0);

      const submissionResponse = await uploadSubmission(participantApi, {
        problemId: uploadedProblemId,
        competitionId: competition.competition.id,
        teamId: team.team.id,
        filePath: packagedProblem.submissionZipPath,
      });
      await expectStatus(submissionResponse, 200);
      const queuedSubmission = await readJson<{ submission: { id: string; status: string } }>(submissionResponse);
      expect(queuedSubmission.submission.status).toBe('QUEUED');

      const seenStatuses = new Set<string>(['QUEUED']);
      const finalSubmission = await pollUntil(
        async () => {
          const response = await getSubmission(participantApi, queuedSubmission.submission.id);
          await expectStatus(response, 200);
          const body = await readJson<{
            submission: {
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
          description: '等待 evaluate_example 示例提交评测完成',
        },
      );
      expect(seenStatuses.has('QUEUED')).toBe(true);
      expect(seenStatuses.has('JUDGING') || seenStatuses.has('COMPLETED')).toBe(true);
      expect(finalSubmission.status).toBe('COMPLETED');
      expect(finalSubmission.score).toBe(52.5);
      expect(finalSubmission.executionLogs).toContain('最终总和为 52.5');

      const problemsAfterResponse = await listCompetitionProblems(participantApi, competition.competition.id, { limit: 20 });
      await expectStatus(problemsAfterResponse, 200);
      const problemsAfter = await readJson<{
        problems: Array<{ id: string; userBestScore: number }>;
      }>(problemsAfterResponse);
      expect(problemsAfter.problems.find((problem) => problem.id === uploadedProblemId)?.userBestScore).toBe(52.5);
    } finally {
      await Promise.all([
        adminApi.dispose(),
        participantApi.dispose(),
        packagedProblem?.cleanup(),
      ]);
    }
  });
});
