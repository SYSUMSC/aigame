import prisma from '~/server/utils/prisma';
import type { Invitation, Team, User } from '@prisma/client';
import { InvitationStatus } from '@prisma/client';

export default defineEventHandler(async (event) => {
  const { id } = event.context.params as { id: string };
  const user = event.context.user;

  if (!user) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized',
    });
  }

  const invitation = await prisma.invitation.findUnique({
    where: {
      id,
    },
    include: {
      team: {
        select: {
          id: true,
          name: true,
        },
      },
      invitedBy: {
        select: {
          id: true,
          realName: true,
          username: true,
        },
      },
    },
  });

  if (!invitation || invitation.inviteeId !== user.id) {
    throw createError({
      statusCode: 404,
      statusMessage: 'Invitation not found',
    });
  }

  return invitation;
});