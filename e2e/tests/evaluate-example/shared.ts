import path from 'node:path';
import { expect, type TestInfo } from '@playwright/test';
import { expectStatus, readJson } from '../../utils/apiClient';
import { createAdminApiContext, createRegisteredUserApiContext } from '../../utils/auth';
import { createCompetition, createTeam, joinCompetition, type CompetitionPayload } from '../../utils/domain';
import { createTestUser } from '../../utils/factory';
import { getProblemDetail, listCompetitionProblems, batchUploadProblems } from '../../utils/problem';
import { pollUntil } from '../../utils/polling';
import { buildPackagedProblemFromExample, type BuiltPackagedExampleArchive } from '../../utils/problemPackage';
import { getSubmission, uploadSubmission } from '../../utils/submission';
import { getRepoRoot, readRuntimeState } from '../../utils/runtime';
import type { EvaluateExampleCase } from './cases';

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

export async function runEvaluateExampleCase(exampleCase: EvaluateExampleCase, testInfo: TestInfo): Promise<void> {
  const adminApi = await createAdminApiContext();
  const { runId } = await readRuntimeState();
  const prefix = `e2e_${runId}_${exampleCase.directoryName}_retry${testInfo.retry}`;
  const problemTitle = `${prefix}_${exampleCase.directoryName}`;
  const userTag = `ee_${exampleCase.directoryName.replace(/[^a-zA-Z0-9]/g, '').slice(0, 12)}`.toLowerCase();
  const participant = await createTestUser(userTag);
  const participantApi = await createRegisteredUserApiContext(participant, { activate: true });
  let packagedProblem: BuiltPackagedExampleArchive | null = null;

  try {
    const competitionResponse = await createCompetition(adminApi, buildCompetitionPayload(`${prefix}_competition`, -60, 360));
    await expectStatus(competitionResponse, 200);
    const competition = await readJson<{ competition: { id: string } }>(competitionResponse);

    packagedProblem = await buildPackagedProblemFromExample(
      path.join(getRepoRoot(), 'evaluate_example', exampleCase.directoryName),
      {
        archiveName: `${prefix}_package`,
        taskDirName: `${prefix}_dir`,
        title: problemTitle,
        shortDescription: `E2E 验证：${exampleCase.displayName}`,
        detailedDescription: `E2E staging 包：来自 evaluate_example/${exampleCase.directoryName}，用于验证题目上传与 test_submit.zip 提交。`,
        startTime: new Date(Date.now() - 20 * 60_000).toISOString(),
        endTime: new Date(Date.now() + 200 * 60_000).toISOString(),
        score: exampleCase.problemScore,
      },
    );

    const uploadResponse = await batchUploadProblems(adminApi, competition.competition.id, 'create', packagedProblem.archivePath);
    await expectStatus(uploadResponse, 200);
    const uploadResult = await readJson<{ results: Array<{ problemId: string; title: string; mode: string }> }>(uploadResponse);
    expect(uploadResult.results).toHaveLength(1);
    expect(uploadResult.results[0]?.mode).toBe('created');
    expect(uploadResult.results[0]?.title).toBe(problemTitle);
    const uploadedProblemId = uploadResult.results[0]!.problemId;

    const problemDetailResponse = await getProblemDetail(adminApi, uploadedProblemId);
    await expectStatus(problemDetailResponse, 200);
    const problemDetail = await readJson<{
      problem: {
        id: string;
        title: string;
        score: number;
        datasetUrl: string | null;
        sampleSubmissionUrl: string | null;
        detailedDescription: string;
      };
    }>(problemDetailResponse);
    expect(problemDetail.problem.id).toBe(uploadedProblemId);
    expect(problemDetail.problem.title).toBe(problemTitle);
    expect(problemDetail.problem.score).toBe(exampleCase.problemScore);
    if (exampleCase.expectsDataset) {
      expect(problemDetail.problem.datasetUrl).toContain('/aigame/problems/datasets/');
    } else {
      expect(problemDetail.problem.datasetUrl).toBeNull();
    }
    expect(problemDetail.problem.sampleSubmissionUrl).toContain('/aigame/problems/samples/');
    expect(problemDetail.problem.detailedDescription).toContain(`evaluate_example/${exampleCase.directoryName}`);

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
    expect(uploadedProblem?.title).toBe(problemTitle);
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
        timeoutMs: 180_000,
        intervalMs: 1_500,
        description: `等待 ${exampleCase.directoryName} 示例提交评测完成`,
      },
    );

    expect(seenStatuses.has('QUEUED')).toBe(true);
    expect(seenStatuses.has('JUDGING') || seenStatuses.has('COMPLETED')).toBe(true);
    expect(finalSubmission.status).toBe('COMPLETED');
    expect(finalSubmission.score).not.toBeNull();
    expect(Number.isFinite(finalSubmission.score ?? Number.NaN)).toBe(true);
    expect(finalSubmission.executionLogs).toContain(exampleCase.successLogSnippet);

    const finalScore = finalSubmission.score as number;
    const problemsAfterResponse = await listCompetitionProblems(participantApi, competition.competition.id, { limit: 20 });
    await expectStatus(problemsAfterResponse, 200);
    const problemsAfter = await readJson<{
      problems: Array<{ id: string; userBestScore: number }>;
    }>(problemsAfterResponse);
    expect(problemsAfter.problems.find((problem) => problem.id === uploadedProblemId)?.userBestScore).toBeCloseTo(finalScore, 5);
  } finally {
    await Promise.all([
      adminApi.dispose(),
      participantApi.dispose(),
      packagedProblem?.cleanup(),
    ]);
  }
}
