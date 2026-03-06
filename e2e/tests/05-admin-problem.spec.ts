import { expect, test } from '@playwright/test';
import { expectStatus, readJson } from '../utils/apiClient';
import { createAdminApiContext } from '../utils/auth';
import { createCompetition, type CompetitionPayload } from '../utils/domain';
import { sampleFiles } from '../fixtures/files';
import { batchUploadProblems, createProblem, deleteProblem, getProblemDetail, listAdminProblems, updateProblem, uploadProblemDataset, uploadProblemSample, uploadProblemScript } from '../utils/problem';
import { buildProblemArchiveFromExample, type BuiltProblemArchive } from '../utils/problemPackage';
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

test.describe('05-管理端题目', () => {
  test('单题与批量上传覆盖资源上传、时间校验、创建编辑删除与覆盖更新', async () => {
    const adminApi = await createAdminApiContext();
    const { runId, files } = await readRuntimeState();
    const prefix = `e2e_${runId}_problem`;
    const createdArchives: BuiltProblemArchive[] = [];

    try {
      const competitionResponse = await createCompetition(
        adminApi,
        buildCompetitionPayload(`${prefix}_competition`, -60, 360),
      );
      await expectStatus(competitionResponse, 200);
      const competition = await readJson<{ competition: { id: string; startTime: string; endTime: string } }>(competitionResponse);

      const datasetUploadResponse = await uploadProblemDataset(adminApi, files.judgeZip);
      const scriptUploadResponse = await uploadProblemScript(adminApi, files.judgeZip);
      const sampleUploadResponse = await uploadProblemSample(adminApi, files.submissionZip);
      await expectStatus(datasetUploadResponse, 200);
      await expectStatus(scriptUploadResponse, 200);
      await expectStatus(sampleUploadResponse, 200);

      const datasetUpload = await readJson<{ url: string }>(datasetUploadResponse);
      const scriptUpload = await readJson<{ url: string }>(scriptUploadResponse);
      const sampleUpload = await readJson<{ url: string }>(sampleUploadResponse);
      expect(datasetUpload.url).toContain('/aigame/problems/datasets/');
      expect(scriptUpload.url).toContain('/aigame/problems/scripts/');
      expect(sampleUpload.url).toContain('/aigame/problems/samples/');

      const invalidProblemResponse = await createProblem(adminApi, competition.competition.id, {
        title: `${prefix}_invalid_range`,
        shortDescription: '超出比赛时间范围',
        detailedDescription: '这个题目故意放在比赛开始之前',
        datasetUrl: datasetUpload.url,
        judgingScriptUrl: scriptUpload.url,
        sampleSubmissionUrl: sampleUpload.url,
        startTime: new Date(new Date(competition.competition.startTime).getTime() - 60 * 60_000).toISOString(),
        endTime: new Date(new Date(competition.competition.startTime).getTime() - 30 * 60_000).toISOString(),
        score: 100,
      });
      await expectStatus(invalidProblemResponse, 400);

      const createdProblemResponse = await createProblem(adminApi, competition.competition.id, {
        title: `${prefix}_single`,
        shortDescription: '单题创建',
        detailedDescription: '用于覆盖管理端单题创建流程',
        datasetUrl: datasetUpload.url,
        judgingScriptUrl: scriptUpload.url,
        sampleSubmissionUrl: sampleUpload.url,
        startTime: new Date(new Date(competition.competition.startTime).getTime() + 10 * 60_000).toISOString(),
        endTime: new Date(new Date(competition.competition.endTime).getTime() - 10 * 60_000).toISOString(),
        score: 200,
      });
      await expectStatus(createdProblemResponse, 200);
      const createdProblem = await readJson<{ problem: { id: string } }>(createdProblemResponse);

      const listedProblemsResponse = await listAdminProblems(adminApi, { competitionId: competition.competition.id, limit: 20 });
      await expectStatus(listedProblemsResponse, 200);
      const listedProblems = await readJson<{ problems: Array<{ id: string; title: string }> }>(listedProblemsResponse);
      expect(listedProblems.problems.some((problem) => problem.id === createdProblem.problem.id)).toBe(true);

      const invalidUpdateResponse = await updateProblem(adminApi, createdProblem.problem.id, {
        title: `${prefix}_single`,
        shortDescription: '更新失败',
        detailedDescription: '结束时间早于开始时间',
        datasetUrl: datasetUpload.url,
        judgingScriptUrl: scriptUpload.url,
        sampleSubmissionUrl: sampleUpload.url,
        startTime: new Date(Date.now() + 90 * 60_000).toISOString(),
        endTime: new Date(Date.now() + 30 * 60_000).toISOString(),
        score: 200,
      });
      await expectStatus(invalidUpdateResponse, 400);

      const updatedTitle = `${prefix}_single_updated`;
      const validUpdateResponse = await updateProblem(adminApi, createdProblem.problem.id, {
        title: updatedTitle,
        shortDescription: '单题更新',
        detailedDescription: '用于覆盖题目编辑流程',
        datasetUrl: datasetUpload.url,
        judgingScriptUrl: scriptUpload.url,
        sampleSubmissionUrl: sampleUpload.url,
        startTime: new Date(new Date(competition.competition.startTime).getTime() + 20 * 60_000).toISOString(),
        endTime: new Date(new Date(competition.competition.endTime).getTime() - 20 * 60_000).toISOString(),
        score: 300,
      });
      await expectStatus(validUpdateResponse, 200);

      const publicProblemResponse = await getProblemDetail(adminApi, createdProblem.problem.id);
      await expectStatus(publicProblemResponse, 200);
      const publicProblem = await readJson<{
        problem: {
          title: string;
          score: number;
          datasetUrl: string | null;
          sampleSubmissionUrl: string | null;
          detailedDescription: string;
        };
      }>(publicProblemResponse);
      expect(publicProblem.problem.title).toBe(updatedTitle);
      expect(publicProblem.problem.score).toBe(300);
      expect(publicProblem.problem.datasetUrl).toBe(datasetUpload.url);
      expect(publicProblem.problem.sampleSubmissionUrl).toBe(sampleUpload.url);

      const createArchive = await buildProblemArchiveFromExample(sampleFiles.judgeSumDir, {
        archiveName: `${prefix}_batch_create`,
        title: `${prefix}_batch_title`,
        shortDescription: '批量创建版本',
        detailedDescription: '这是批量创建版本的题目详情',
        startTime: new Date(Date.now() - 20 * 60_000).toISOString(),
        endTime: new Date(Date.now() + 200 * 60_000).toISOString(),
        score: 123,
      });
      createdArchives.push(createArchive);

      const batchCreateResponse = await batchUploadProblems(adminApi, competition.competition.id, 'create', createArchive.archivePath);
      await expectStatus(batchCreateResponse, 200);
      const batchCreate = await readJson<{ results: Array<{ problemId: string; title: string; mode: string }> }>(batchCreateResponse);
      expect(batchCreate.results).toHaveLength(1);
      expect(batchCreate.results[0]?.mode).toBe('created');

      const overwriteArchive = await buildProblemArchiveFromExample(sampleFiles.judgeSumDir, {
        archiveName: `${prefix}_batch_overwrite`,
        title: `${prefix}_batch_title`,
        shortDescription: '批量覆盖版本',
        detailedDescription: '这是批量覆盖版本的题目详情',
        startTime: new Date(Date.now() - 10 * 60_000).toISOString(),
        endTime: new Date(Date.now() + 300 * 60_000).toISOString(),
        score: 321,
      });
      createdArchives.push(overwriteArchive);

      const batchOverwriteResponse = await batchUploadProblems(adminApi, competition.competition.id, 'overwrite', overwriteArchive.archivePath);
      await expectStatus(batchOverwriteResponse, 200);
      const batchOverwrite = await readJson<{ results: Array<{ problemId: string; title: string; mode: string }> }>(batchOverwriteResponse);
      expect(batchOverwrite.results).toHaveLength(1);
      expect(batchOverwrite.results[0]?.mode).toBe('updated');

      const overwrittenProblemResponse = await getProblemDetail(adminApi, batchOverwrite.results[0]!.problemId);
      await expectStatus(overwrittenProblemResponse, 200);
      const overwrittenProblem = await readJson<{ problem: { score: number; detailedDescription: string } }>(overwrittenProblemResponse);
      expect(overwrittenProblem.problem.score).toBe(321);
      expect(overwrittenProblem.problem.detailedDescription).toContain('批量覆盖版本');

      const deleteResponse = await deleteProblem(adminApi, createdProblem.problem.id);
      await expectStatus(deleteResponse, 200);

      const deletedProblemResponse = await getProblemDetail(adminApi, createdProblem.problem.id);
      await expectStatus(deletedProblemResponse, 404);
    } finally {
      await Promise.all(createdArchives.map((archive) => archive.cleanup()));
      await adminApi.dispose();
    }
  });
});
