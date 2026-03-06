import { defineEventHandler, getQuery } from 'h3'
import prisma from '../../../utils/prisma'
import { requireAdminRole } from '../../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = event.context.user
  if (!user) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Authentication required'
    })
  }

  // Check admin role
  requireAdminRole(user)

  // Get query parameters for pagination and search
  const query = getQuery(event)
  const page = parseInt(query.page as string) || 1
  const limit = parseInt(query.limit as string) || 10
  const id = query.id as string || ''
  const username = query.user as string || ''
  const team = query.team as string || ''
  const problem = query.problem as string || ''
  const competition = query.competition as string || ''
  const skip = (page - 1) * limit

  // Build search conditions
  const where: any = {}
  const AND: any[] = []

  if (id) {
    // Mongo ObjectId 字段不支持 contains，管理端按精确 ID 查询即可。
    AND.push({ id })
  }

  if (username) {
    AND.push({ user: { username: { contains: username, mode: 'insensitive' } } })
  }

  if (team) {
    AND.push({ team: { name: { contains: team, mode: 'insensitive' } } })
  }

  if (problem) {
    AND.push({ problem: { title: { contains: problem, mode: 'insensitive' } } })
  }

  if (competition) {
    AND.push({ competition: { title: { contains: competition, mode: 'insensitive' } } })
  }

  if (AND.length > 0) {
    where.AND = AND
  }

  // Get total count
  const total = await prisma.submission.count({ where })

  // Get submissions with pagination
  const submissions = await prisma.submission.findMany({
    where,
    skip,
    take: limit,
    orderBy: {
      createdAt: 'desc',
    },
    include: {
      user: {
        select: {
          id: true,
          username: true,
        },
      },
      team: {
        select: {
          id: true,
          name: true,
        },
      },
      problem: {
        select: {
          id: true,
          title: true,
        },
      },
      competition: {
        select: {
          id: true,
          title: true,
        },
      },
    },
  })

  // Calculate pagination info
  const totalPages = Math.ceil(total / limit)

  return {
    submissions,
    pagination: {
      page,
      limit,
      total,
      totalPages
    }
  }
})