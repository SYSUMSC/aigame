import { z } from 'zod'
import { verifyPassword, excludePassword, checkUserCanLogin, shouldUseSecureCookie } from '../../utils/auth'
import { generateToken } from '../../utils/jwt'
import prisma from '../../utils/prisma'

const loginSchema = z.object({
  identifier: z.string().min(1), // 可以是邮箱或用户名
  password: z.string().min(1)
})

export default defineEventHandler(async (event) => {
  if (event.method !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method not allowed'
    })
  }

  const body = await readBody(event)

  try {
    const { identifier, password } = loginSchema.parse(body)



    // 判断输入的是邮箱还是用户名
    const isEmail = identifier.includes('@')

    // 根据输入类型查找用户
    const user = await prisma.user.findUnique({
      where: isEmail ? { email: identifier } : { username: identifier }
    })

    if (!user) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Invalid credentials'
      })
    }

    // Verify password
    const isValidPassword = await verifyPassword(password, user.passwordHash)

    if (!isValidPassword) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Invalid credentials'
      })
    }

    // Check user status
    checkUserCanLogin(user)

    // Generate JWT token
    const token = generateToken(user)
    const safeUser = excludePassword(user)

    // Set HTTP-only cookie
    setCookie(event, 'auth-token', token, {
      httpOnly: true,
      secure: shouldUseSecureCookie(event),
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7 // 7 days
    })

    return {
      success: true,
      user: safeUser,
      token
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