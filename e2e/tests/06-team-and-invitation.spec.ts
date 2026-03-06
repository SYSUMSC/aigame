import { expect, test } from '@playwright/test';
import { expectStatus, readJson } from '../utils/apiClient';
import { createAdminApiContext, createRegisteredUserApiContext } from '../utils/auth';
import { createTestUser } from '../utils/factory';
import { acceptInvitation, createCompetition, createTeam, getInvitation, getTeam, inviteMember, joinCompetition, leaveTeam, rejectInvitation, removeTeamMember, type CompetitionPayload } from '../utils/domain';
import { readRuntimeState } from '../utils/runtime';

function ongoingCompetitionPayload(title: string): CompetitionPayload {
  const now = Date.now();
  return {
    title,
    description: `${title} description`,
    rules: `${title} rules`,
    startTime: new Date(now - 30 * 60_000).toISOString(),
    endTime: new Date(now + 2 * 60 * 60_000).toISOString(),
  };
}

test.describe('06-队伍与邀请', () => {
  test('队伍创建冲突、邀请接受拒绝、队长权限与锁队限制都能覆盖', async () => {
    const { runId } = await readRuntimeState();
    const adminApi = await createAdminApiContext();

    const captain = await createTestUser('team-captain');
    const invitee = await createTestUser('team-invitee');
    const rejectUser = await createTestUser('team-reject');
    const outsider = await createTestUser('team-outsider');
    const lateInvitee = await createTestUser('team-late');

    const captainApi = await createRegisteredUserApiContext(captain, { activate: true });
    const inviteeApi = await createRegisteredUserApiContext(invitee, { activate: true });
    const rejectApi = await createRegisteredUserApiContext(rejectUser, { activate: true });
    const outsiderApi = await createRegisteredUserApiContext(outsider, { activate: true });
    const lateInviteeApi = await createRegisteredUserApiContext(lateInvitee, { activate: true });

    const teamName = `e2e_${runId}_team_main`;
    const createResponse = await createTeam(captainApi, teamName);
    await expectStatus(createResponse, 200);
    const createdTeam = await readJson<{ team: { id: string; name: string } }>(createResponse);

    const duplicateResponse = await createTeam(outsiderApi, teamName);
    await expectStatus(duplicateResponse, 409);

    const outsiderInviteResponse = await inviteMember(outsiderApi, createdTeam.team.id, invitee.email);
    await expectStatus(outsiderInviteResponse, 403);

    const inviteResponse = await inviteMember(captainApi, createdTeam.team.id, invitee.email);
    await expectStatus(inviteResponse, 200);
    const invitation = await readJson<{ invitation: { id: string } }>(inviteResponse);

    const getInvitationResponse = await getInvitation(inviteeApi, invitation.invitation.id);
    await expectStatus(getInvitationResponse, 200);

    const acceptResponse = await acceptInvitation(inviteeApi, invitation.invitation.id);
    await expectStatus(acceptResponse, 200);

    const inviteeMeResponse = await inviteeApi.get('/api/auth/me');
    await expectStatus(inviteeMeResponse, 200);
    const inviteeMe = await readJson<{ user: { id: string } }>(inviteeMeResponse);

    const teamAfterAcceptResponse = await getTeam(captainApi, createdTeam.team.id);
    await expectStatus(teamAfterAcceptResponse, 200);
    const teamAfterAccept = await readJson<{ team: { members: Array<{ user: { email: string } }> } }>(teamAfterAcceptResponse);
    expect(teamAfterAccept.team.members.some((member: { user: { email: string } }) => member.user.email === invitee.email)).toBe(true);

    const secondInviteResponse = await inviteMember(captainApi, createdTeam.team.id, rejectUser.email);
    await expectStatus(secondInviteResponse, 200);
    const secondInvitation = await readJson<{ invitation: { id: string } }>(secondInviteResponse);

    const rejectResponse = await rejectInvitation(rejectApi, secondInvitation.invitation.id);
    await expectStatus(rejectResponse, 200);

    const rejectedInvitationResponse = await getInvitation(rejectApi, secondInvitation.invitation.id);
    await expectStatus(rejectedInvitationResponse, 200);
    const rejectedInvitation = await readJson<{ status: string }>(rejectedInvitationResponse);
    expect(rejectedInvitation.status).toBe('REJECTED');

    const removeMemberResponse = await removeTeamMember(captainApi, createdTeam.team.id, inviteeMe.user.id);
    await expectStatus(removeMemberResponse, 200);

    const reInviteResponse = await inviteMember(captainApi, createdTeam.team.id, invitee.email);
    await expectStatus(reInviteResponse, 200);
    const reInvitation = await readJson<{ invitation: { id: string } }>(reInviteResponse);
    await expectStatus(await acceptInvitation(inviteeApi, reInvitation.invitation.id), 200);

    const nonCaptainInviteResponse = await inviteMember(inviteeApi, createdTeam.team.id, lateInvitee.email);
    await expectStatus(nonCaptainInviteResponse, 403);

    const competitionResponse = await createCompetition(adminApi, ongoingCompetitionPayload(`e2e_${runId}_team_lock_comp`));
    await expectStatus(competitionResponse, 200);
    const competition = await readJson<{ competition: { id: string } }>(competitionResponse);

    const joinResponse = await joinCompetition(captainApi, competition.competition.id, createdTeam.team.id);
    await expectStatus(joinResponse, 200);
    const joinedTeam = await readJson<{ team: { isLocked: boolean } }>(joinResponse);
    expect(joinedTeam.team.isLocked).toBe(true);

    const lockedInviteResponse = await inviteMember(captainApi, createdTeam.team.id, lateInvitee.email);
    await expectStatus(lockedInviteResponse, 403);

    const lockedRemoveResponse = await removeTeamMember(captainApi, createdTeam.team.id, inviteeMe.user.id);
    await expectStatus(lockedRemoveResponse, 403);

    const lockedLeaveResponse = await leaveTeam(inviteeApi, createdTeam.team.id);
    await expectStatus(lockedLeaveResponse, 403);

    await Promise.all([
      adminApi.dispose(),
      captainApi.dispose(),
      inviteeApi.dispose(),
      rejectApi.dispose(),
      outsiderApi.dispose(),
      lateInviteeApi.dispose(),
    ]);
  });
});
