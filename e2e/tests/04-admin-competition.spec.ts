import { expect, test } from '@playwright/test';
import { expectStatus, readJson } from '../utils/apiClient';
import { createAdminApiContext } from '../utils/auth';
import { createCompetition, deleteCompetition, getCompetition, listAdminCompetitions, updateCompetition, type CompetitionPayload } from '../utils/domain';
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

test.describe('04-管理端比赛', () => {
  test('比赛管理覆盖创建、编辑、筛选、分页、校验与删除', async () => {
    const adminApi = await createAdminApiContext();
    const { runId } = await readRuntimeState();
    const prefix = `e2e_${runId}_comp`;

    const invalidResponse = await createCompetition(
      adminApi,
      buildCompetitionPayload(`${prefix}_invalid`, 120, 60),
    );
    await expectStatus(invalidResponse, 400);

    const upcomingPayload = buildCompetitionPayload(`${prefix}_upcoming`, 180, 300);
    const ongoingPayload = buildCompetitionPayload(`${prefix}_ongoing`, -30, 180);
    const endedPayload = buildCompetitionPayload(`${prefix}_ended`, -180, -60);
    const deletablePayload = buildCompetitionPayload(`${prefix}_deletable`, 360, 480);

    const upcomingResponse = await createCompetition(adminApi, upcomingPayload);
    const ongoingResponse = await createCompetition(adminApi, ongoingPayload);
    const endedResponse = await createCompetition(adminApi, endedPayload);
    const deletableResponse = await createCompetition(adminApi, deletablePayload);

    await expectStatus(upcomingResponse, 200);
    await expectStatus(ongoingResponse, 200);
    await expectStatus(endedResponse, 200);
    await expectStatus(deletableResponse, 200);

    const upcoming = await readJson<{ competition: { id: string } }>(upcomingResponse);
    const ongoing = await readJson<{ competition: { id: string } }>(ongoingResponse);
    const ended = await readJson<{ competition: { id: string } }>(endedResponse);
    const deletable = await readJson<{ competition: { id: string } }>(deletableResponse);

    const updatedTitle = `${prefix}_ongoing_updated`;
    const updateResponse = await updateCompetition(adminApi, ongoing.competition.id, {
      ...ongoingPayload,
      title: updatedTitle,
      description: 'updated description',
      rules: 'updated rules',
      solutionSubmissionDeadlineDays: 5,
    });
    await expectStatus(updateResponse, 200);

    const getUpdatedResponse = await getCompetition(adminApi, ongoing.competition.id);
    await expectStatus(getUpdatedResponse, 200);
    const updated = await readJson<{ competition: { title: string; description: string; solutionSubmissionDeadlineDays: number } }>(getUpdatedResponse);
    expect(updated.competition.title).toBe(updatedTitle);
    expect(updated.competition.description).toBe('updated description');
    expect(updated.competition.solutionSubmissionDeadlineDays).toBe(5);

    const upcomingListResponse = await listAdminCompetitions(adminApi, { status: 'upcoming', limit: 10 });
    await expectStatus(upcomingListResponse, 200);
    const upcomingList = await readJson<{ competitions: Array<{ title: string }> }>(upcomingListResponse);
    expect(upcomingList.competitions.some((competition: { title: string }) => competition.title === upcomingPayload.title)).toBe(true);
    expect(upcomingList.competitions.some((competition: { title: string }) => competition.title === deletablePayload.title)).toBe(true);

    const ongoingListResponse = await listAdminCompetitions(adminApi, { status: 'ongoing', limit: 10 });
    await expectStatus(ongoingListResponse, 200);
    const ongoingList = await readJson<{ competitions: Array<{ title: string }> }>(ongoingListResponse);
    expect(ongoingList.competitions.some((competition: { title: string }) => competition.title === updatedTitle)).toBe(true);

    const endedListResponse = await listAdminCompetitions(adminApi, { status: 'ended', limit: 10 });
    await expectStatus(endedListResponse, 200);
    const endedList = await readJson<{ competitions: Array<{ title: string }> }>(endedListResponse);
    expect(endedList.competitions.some((competition: { title: string }) => competition.title === endedPayload.title)).toBe(true);

    const pageOneResponse = await listAdminCompetitions(adminApi, { page: 1, limit: 2 });
    const pageTwoResponse = await listAdminCompetitions(adminApi, { page: 2, limit: 2 });
    await expectStatus(pageOneResponse, 200);
    await expectStatus(pageTwoResponse, 200);
    const pageOne = await readJson<{ competitions: Array<{ id: string }>; pagination: { page: number; limit: number; totalPages: number } }>(pageOneResponse);
    const pageTwo = await readJson<{ competitions: Array<{ id: string }>; pagination: { page: number; limit: number; totalPages: number } }>(pageTwoResponse);
    expect(pageOne.pagination.page).toBe(1);
    expect(pageOne.pagination.limit).toBe(2);
    expect(pageTwo.pagination.page).toBe(2);
    expect(pageOne.pagination.totalPages).toBeGreaterThanOrEqual(2);
    expect(pageOne.competitions.map((competition: { id: string }) => competition.id)).not.toEqual(pageTwo.competitions.map((competition: { id: string }) => competition.id));

    const deleteResponse = await deleteCompetition(adminApi, deletable.competition.id);
    await expectStatus(deleteResponse, 200);
    const getDeletedResponse = await getCompetition(adminApi, deletable.competition.id);
    await expectStatus(getDeletedResponse, 404);

    await adminApi.dispose();

    expect([upcoming.competition.id, ongoing.competition.id, ended.competition.id]).toHaveLength(3);
  });
});
