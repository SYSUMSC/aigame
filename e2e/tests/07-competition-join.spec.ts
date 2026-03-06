import { expect, test } from '@playwright/test';
import { expectStatus, readJson } from '../utils/apiClient';
import { createAdminApiContext, createRegisteredUserApiContext } from '../utils/auth';
import { createTestUser } from '../utils/factory';
import { acceptInvitation, createCompetition, createTeam, inviteMember, joinCompetition, type CompetitionPayload } from '../utils/domain';
import { readRuntimeState } from '../utils/runtime';

function competitionPayload(title: string, startOffsetMinutes: number, endOffsetMinutes: number): CompetitionPayload {
  const now = Date.now();
  return {
    title,
    description: `${title} description`,
    rules: `${title} rules`,
    startTime: new Date(now + startOffsetMinutes * 60_000).toISOString(),
    endTime: new Date(now + endOffsetMinutes * 60_000).toISOString(),
  };
}

test.describe('07-比赛报名', () => {
  test('报名成功、时间窗口失败、成员重复冲突与非成员拒绝都能覆盖', async () => {
    const { runId } = await readRuntimeState();
    const adminApi = await createAdminApiContext();

    const captainOne = await createTestUser('join-captain-one');
    const captainTwo = await createTestUser('join-captain-two');
    const sharedMember = await createTestUser('join-member');
    const outsider = await createTestUser('join-outsider');

    const captainOneApi = await createRegisteredUserApiContext(captainOne, { activate: true });
    const captainTwoApi = await createRegisteredUserApiContext(captainTwo, { activate: true });
    const sharedMemberApi = await createRegisteredUserApiContext(sharedMember, { activate: true });
    const outsiderApi = await createRegisteredUserApiContext(outsider, { activate: true });

    const teamOneResponse = await createTeam(captainOneApi, `e2e_${runId}_join_team_one`);
    const teamTwoResponse = await createTeam(captainTwoApi, `e2e_${runId}_join_team_two`);
    await expectStatus(teamOneResponse, 200);
    await expectStatus(teamTwoResponse, 200);
    const teamOne = await readJson<{ team: { id: string } }>(teamOneResponse);
    const teamTwo = await readJson<{ team: { id: string } }>(teamTwoResponse);

    const inviteOneResponse = await inviteMember(captainOneApi, teamOne.team.id, sharedMember.email);
    const inviteTwoResponse = await inviteMember(captainTwoApi, teamTwo.team.id, sharedMember.email);
    await expectStatus(inviteOneResponse, 200);
    await expectStatus(inviteTwoResponse, 200);
    const invitationOne = await readJson<{ invitation: { id: string } }>(inviteOneResponse);
    const invitationTwo = await readJson<{ invitation: { id: string } }>(inviteTwoResponse);
    await expectStatus(await acceptInvitation(sharedMemberApi, invitationOne.invitation.id), 200);
    await expectStatus(await acceptInvitation(sharedMemberApi, invitationTwo.invitation.id), 200);

    const upcomingResponse = await createCompetition(adminApi, competitionPayload(`e2e_${runId}_join_upcoming`, 120, 240));
    const ongoingResponse = await createCompetition(adminApi, competitionPayload(`e2e_${runId}_join_ongoing`, -30, 180));
    const endedResponse = await createCompetition(adminApi, competitionPayload(`e2e_${runId}_join_ended`, -180, -60));
    await expectStatus(upcomingResponse, 200);
    await expectStatus(ongoingResponse, 200);
    await expectStatus(endedResponse, 200);
    const upcoming = await readJson<{ competition: { id: string } }>(upcomingResponse);
    const ongoing = await readJson<{ competition: { id: string } }>(ongoingResponse);
    const ended = await readJson<{ competition: { id: string } }>(endedResponse);

    const upcomingJoinResponse = await joinCompetition(captainOneApi, upcoming.competition.id, teamOne.team.id);
    await expectStatus(upcomingJoinResponse, 400);

    const endedJoinResponse = await joinCompetition(captainOneApi, ended.competition.id, teamOne.team.id);
    await expectStatus(endedJoinResponse, 400);

    const outsiderJoinResponse = await joinCompetition(outsiderApi, ongoing.competition.id, teamOne.team.id);
    await expectStatus(outsiderJoinResponse, 403);

    const successJoinResponse = await joinCompetition(captainOneApi, ongoing.competition.id, teamOne.team.id);
    await expectStatus(successJoinResponse, 200);
    const joined = await readJson<{ team: { isLocked: boolean; participatingIn: string[] } }>(successJoinResponse);
    expect(joined.team.isLocked).toBe(true);
    expect(joined.team.participatingIn).toContain(ongoing.competition.id);

    const duplicateMemberJoinResponse = await joinCompetition(captainTwoApi, ongoing.competition.id, teamTwo.team.id);
    await expectStatus(duplicateMemberJoinResponse, 400);

    await Promise.all([
      adminApi.dispose(),
      captainOneApi.dispose(),
      captainTwoApi.dispose(),
      sharedMemberApi.dispose(),
      outsiderApi.dispose(),
    ]);
  });
});
