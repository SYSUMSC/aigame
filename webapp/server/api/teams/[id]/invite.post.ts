import { z } from 'zod'
import prisma from '~/server/utils/prisma'
import { sendInvitationEmail } from '~/server/utils/email'

const inviteSchema = z.object({
  email: z.string().email()
})

export default defineEventHandler(async (event) => {
  if (event.method !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method not allowed'
    })
  }

  const user = event.context.user
  if (!user) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Authentication required'
    })
  }

  const teamId = getRouterParam(event, 'id')
  const body = await readBody(event)

  try {
    const { email } = inviteSchema.parse(body)

    const team = await prisma.team.findUnique({
      where: { id: teamId },
      include: {
        members: {
          include: {
            user: true
          }
        }
      }
    })

    if (!team) {
      throw createError({
        statusCode: 404,
        statusMessage: 'Team not found'
      })
    }

    const userMembership = team.members.find(member => member.userId === user.id)
    if (!userMembership || userMembership.role !== 'CREATOR') {
      throw createError({
        statusCode: 403,
        statusMessage: '只有队长可以邀请成员'
      })
    }

    if (team.isLocked) {
      throw createError({
        statusCode: 403,
        statusMessage: '无法修改已锁定的队伍'
      })
    }

    const userToInvite = await prisma.user.findUnique({
      where: { email }
    })

    if (!userToInvite) {
      throw createError({
        statusCode: 404,
        statusMessage: 'User not found'
      })
    }

    const existingMember = team.members.find(member => member.userId === userToInvite.id)
    if (existingMember) {
      throw createError({
        statusCode: 409,
        statusMessage: 'User is already a team member'
      })
    }

    const existingInvitation = await prisma.invitation.findFirst({
      where: {
        teamId: team.id,
        inviteeId: userToInvite.id,
        status: 'PENDING'
      }
    })

    if (existingInvitation) {
      throw createError({
        statusCode: 409,
        statusMessage: 'An invitation has already been sent to this user'
      })
    }

    const invitation = await prisma.invitation.create({
      data: {
        teamId: team.id,
        invitedById: user.id,
        inviteeId: userToInvite.id
      }
    })

    await sendInvitationEmail(invitation.id, userToInvite.email, team.name, user.username)

    return {
      success: true,
      invitation
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Validation failed',
        data: error.issues
      })
    }

    throw error
  }
})
