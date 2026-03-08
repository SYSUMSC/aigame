import bcrypt from 'bcryptjs'
import type { User } from '@prisma/client'
import type { H3Event } from 'h3'
import { createError, getHeader } from 'h3'

export async function hashPassword(password: string): Promise<string> {
  const saltRounds = 12
  return await bcrypt.hash(password, saltRounds)
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return await bcrypt.compare(password, hash)
}

export function excludePassword<T extends Record<string, any>>(
  user: T
): Omit<T, 'passwordHash'> {
  const { passwordHash, ...userWithoutPassword } = user
  return userWithoutPassword
}

export function requireAdminRole(user: User): void {
  if (user.role !== 'admin') {
    throw createError({
      statusCode: 403,
      statusMessage: 'Forbidden: Admin access required'
    })
  }
}

/**
 * 检查用户是否被封禁
 */
export function checkUserBanned(user: User): void {
  if (user.status === 'BANNED') {
    throw createError({
      statusCode: 403,
      statusMessage: '账号已被封禁，无法访问'
    })
  }
}

/**
 * 检查用户是否为活跃状态（已验证邮箱）
 */
export function requireActiveUser(user: User): void {
  if (user.status === 'PENDING') {
    throw createError({
      statusCode: 403,
      statusMessage: '请先验证邮箱后再进行此操作'
    })
  }

  checkUserBanned(user)
}

/**
 * 检查用户状态是否允许登录
 */
export function checkUserCanLogin(user: User): void {
  if (user.status === 'BANNED') {
    throw createError({
      statusCode: 403,
      statusMessage: '账号已被封禁，无法登录'
    })
  }
}

export type SafeUser = Omit<User, 'passwordHash'>

/**
 * 在 HTTPS、反向代理 HTTPS，或显式要求时启用 Secure Cookie。
 * 这样既兼容线上生产环境，也兼容本地 HTTP 的 E2E / 冒烟环境。
 */
export function shouldUseSecureCookie(event: H3Event): boolean {
  const explicit = process.env.AUTH_COOKIE_SECURE?.trim().toLowerCase()

  if (explicit === 'true') {
    return true
  }

  if (explicit === 'false') {
    return false
  }

  const forwardedProto = getHeader(event, 'x-forwarded-proto')?.split(',')[0]?.trim().toLowerCase()
  if (forwardedProto === 'https') {
    return true
  }

  if (forwardedProto === 'http') {
    return false
  }

  const forwardedSsl = getHeader(event, 'x-forwarded-ssl')?.trim().toLowerCase()
  if (forwardedSsl === 'on') {
    return true
  }

  if (forwardedSsl === 'off') {
    return false
  }

  const origin = getHeader(event, 'origin')?.trim().toLowerCase()
  if (origin?.startsWith('https://')) {
    return true
  }

  if (origin?.startsWith('http://')) {
    return false
  }

  const referer = getHeader(event, 'referer')?.trim().toLowerCase()
  if (referer?.startsWith('https://')) {
    return true
  }

  if (referer?.startsWith('http://')) {
    return false
  }

  const socket = event.node.req.socket as typeof event.node.req.socket & { encrypted?: boolean }
  if (socket.encrypted) {
    return true
  }

  return false
}
