import { z } from 'zod'
import { randomBytes } from 'crypto'
import { sendPasswordReset } from '../../utils/email'
import prisma from '../../utils/prisma'

// 定义请求参数校验规则
const forgotPasswordSchema = z.object({
    email: z.string().email()
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
        // 验证请求参数
        const { email } = forgotPasswordSchema.parse(body)

        // 查找用户
        const user = await prisma.user.findUnique({
            where: { email }
        })

        // 检查用户是否存在
        if (!user) {
            console.log(`密码重置请求 - 用户不存在: ${email}`)
            throw createError({
                statusCode: 404,
                statusMessage: '该邮箱地址未注册，请检查邮箱地址或先注册账户'
            })
        }

        // 验证用户状态
        if (user.status !== 'ACTIVE') {
            console.log(`密码重置请求被拒绝 - 用户状态不是ACTIVE: ${email} (状态: ${user.status})`)
            throw createError({
                statusCode: 403,
                statusMessage: '账户状态异常，无法重置密码。请联系管理员'
            })
        }

        // 生成密码重置令牌（1小时有效期）
        const resetToken = randomBytes(32).toString('hex')
        const resetTokenExpires = new Date(Date.now() + 60 * 60 * 1000) // 1小时后过期

        // 更新用户的重置令牌
        await prisma.user.update({
            where: { email },
            data: {
                passwordResetToken: resetToken,
                passwordResetTokenExpiresAt: resetTokenExpires
            }
        })

        // 发送密码重置邮件
        try {
            const emailSent = await sendPasswordReset(email, resetToken, user.username)
            if (emailSent) {
                console.log(`密码重置邮件发送成功: ${email}`)
            } else {
                console.warn(`密码重置邮件发送失败: ${email}`)
            }
        } catch (emailError) {
            console.error('发送密码重置邮件时出错:', emailError)
            // 邮件发送失败不影响接口响应，但会记录日志
        }

        // 返回成功消息
        return {
            success: true,
            message: '密码重置邮件已发送到您的邮箱，请查收'
        }

    } catch (error: any) {
        if (error instanceof z.ZodError) {
            throw createError({
                statusCode: 400,
                statusMessage: '参数验证失败',
                data: error.issues
            })
        }

        if (error?.statusCode) {
            throw error
        }

        console.error('密码重置请求过程中发生错误:', error)
        throw createError({
            statusCode: 500,
            statusMessage: '服务器内部错误'
        })
    }
})
