import * as nodemailer from 'nodemailer';
import type { Transporter } from 'nodemailer';

// 邮件传输配置接口
interface SMTPConfig {
  host: string;
  port: number;
  user: string;
  pass: string;
  from: string;
  fromName: string;
  secure: boolean;
  tls: boolean;
}

function shouldStubEmail(): boolean {
  return process.env.SMTP_STUB === 'true';
}

// 邮件选项接口
interface EmailOptions {
  to: string;
  subject: string;
  html: string;
  text?: string;
}

// 从环境变量获取邮件传输配置
function getSMTPConfig(): SMTPConfig {
  const config: SMTPConfig = {
    host: process.env.SMTP_HOST || 'localhost',
    port: parseInt(process.env.SMTP_PORT || '587'),
    user: process.env.SMTP_USER || '',
    pass: process.env.SMTP_PASS || '',
    from: process.env.SMTP_FROM || 'noreply@example.com',
    fromName: process.env.SMTP_FROM_NAME || 'AI Game Platform',
    secure: process.env.SMTP_SECURE === 'true',
    tls: process.env.SMTP_TLS !== 'false'
  };

  // 验证必要的配置
  if (!config.host || !config.user || !config.pass || !config.from) {
    console.warn('SMTP配置不完整，邮件发送功能可能无法正常工作');
  }

  return config;
}

// 创建邮件传输器
function createTransporter(): Transporter {
  const config = getSMTPConfig();

  const transportConfig: any = {
    host: config.host,
    port: config.port,
    auth: {
      user: config.user,
      pass: config.pass
    }
  };

  // 根据配置设置安全选项
  if (config.secure) {
    transportConfig.secure = true;
  } else if (config.tls) {
    transportConfig.tls = {
      rejectUnauthorized: false
    };
  }

  return nodemailer.createTransport(transportConfig);
}

// 基础邮件发送函数
export async function sendEmail(options: EmailOptions): Promise<boolean> {
  if (shouldStubEmail()) {
    console.log(`[SMTP_STUB] Skip sending email to ${options.to}: ${options.subject}`);
    return true;
  }

  try {
    const config = getSMTPConfig();
    const transporter = createTransporter();

    const mailOptions = {
      from: `"${config.fromName}" <${config.from}>`,
      to: options.to,
      subject: options.subject,
      html: options.html,
      text: options.text || options.html.replace(/<[^>]*>/g, '') // 如果没有提供纯文本，则从富文本内容中提取
    };

    const info = await transporter.sendMail(mailOptions);
    console.log(`邮件发送成功: ${info.messageId} to ${options.to}`);
    return true;
  } catch (error) {
    console.error('邮件发送失败:', error);
    return false;
  }
}

// 生成富文本邮件模板
function generateEmailTemplate(title: string, content: string, actionUrl?: string, actionText?: string): string {
  return `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${title}</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          line-height: 1.6;
          color: #333;
          background-color: #f4f4f4;
          margin: 0;
          padding: 0;
        }
        .container {
          max-width: 600px;
          margin: 20px auto;
          background-color: #ffffff;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          overflow: hidden;
        }
        .header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 30px;
          text-align: center;
        }
        .header h1 {
          margin: 0;
          font-size: 28px;
          font-weight: 300;
        }
        .content {
          padding: 40px 30px;
        }
        .content h2 {
          color: #333;
          margin-bottom: 20px;
          font-size: 24px;
        }
        .content p {
          margin-bottom: 15px;
          font-size: 16px;
        }
        .action-button {
          display: inline-block;
          padding: 15px 30px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          text-decoration: none;
          border-radius: 5px;
          font-weight: bold;
          margin: 20px 0;
          text-align: center;
        }
        .action-button:hover {
          opacity: 0.9;
        }
        .footer {
          background-color: #f8f9fa;
          padding: 20px 30px;
          text-align: center;
          font-size: 14px;
          color: #666;
          border-top: 1px solid #eee;
        }
        .footer p {
          margin: 5px 0;
        }
        .divider {
          height: 1px;
          background-color: #eee;
          margin: 20px 0;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>AI Game Platform</h1>
        </div>
        <div class="content">
          <h2>${title}</h2>
          ${content}
          ${actionUrl && actionText ? `
            <div style="text-align: center; margin: 30px 0;">
              <a href="${actionUrl}" class="action-button">${actionText}</a>
            </div>
          ` : ''}
        </div>
        <div class="footer">
          <p>此邮件由 AI Game Platform 自动发送</p>
          <p>如果您有任何疑问，请联系我们的技术支持团队</p>
          <p>&copy; ${new Date().getFullYear()} AI Game Platform. All rights reserved.</p>
        </div>
      </div>
    </body>
    </html>
  `;
}

// 发送团队邀请邮件
export async function sendInvitationEmail(invitationId: string, inviteeEmail: string, teamName: string, inviterName: string): Promise<boolean> {
  try {
    const baseUrl = process.env.NUXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    const invitationUrl = `${baseUrl}/invitations/${invitationId}`;

    const content = `
      <p>您好！</p>
      <p><strong>${inviterName}</strong> 邀请您加入团队 <strong>"${teamName}"</strong>。</p>
      <p>加入团队后，您将能够：</p>
      <ul>
        <li>与团队成员协作参加竞赛</li>
        <li>共享竞赛资源和经验</li>
        <li>获得团队积分和排名</li>
      </ul>
      <div class="divider"></div>
      <p><strong>注意：</strong>此邀请链接将在7天后过期，请尽快处理。</p>
    `;

    const emailOptions: EmailOptions = {
      to: inviteeEmail,
      subject: `邀请加入团队：${teamName}`,
      html: generateEmailTemplate(
        '团队邀请',
        content,
        invitationUrl,
        '接受邀请'
      )
    };

    const success = await sendEmail(emailOptions);
    if (success) {
      console.log(`团队邀请邮件已发送: ${inviteeEmail} 加入团队 ${teamName}`);
    }
    return success;
  } catch (error) {
    console.error('发送团队邀请邮件失败:', error);
    return false;
  }
}

// 发送邮箱验证邮件
export async function sendEmailVerification(email: string, token: string, username: string): Promise<boolean> {
  try {
    const baseUrl = process.env.NUXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    const verificationUrl = `${baseUrl}/auth/verify-email?token=${token}&email=${encodeURIComponent(email)}`;

    const content = `
      <p>欢迎您，<strong>${username}</strong>！</p>
      <p>感谢您注册 AI Game Platform。为了确保您的账户安全，请点击下面的按钮验证您的邮箱地址。</p>
      <p>邮箱验证后，您将能够：</p>
      <ul>
        <li>参加各种AI竞赛</li>
        <li>创建或加入团队</li>
        <li>查看详细的排行榜和成绩</li>
        <li>获得竞赛证书和奖励</li>
      </ul>
      <div class="divider"></div>
      <p><strong>注意：</strong>验证链接将在24小时后过期。如果链接过期，请重新注册或联系客服。</p>
    `;

    const emailOptions: EmailOptions = {
      to: email,
      subject: 'AI Game Platform - 邮箱验证',
      html: generateEmailTemplate(
        '邮箱验证',
        content,
        verificationUrl,
        '验证邮箱'
      )
    };

    const success = await sendEmail(emailOptions);
    if (success) {
      console.log(`邮箱验证邮件已发送: ${email} 用户: ${username}`);
    }
    return success;
  } catch (error) {
    console.error('发送邮箱验证邮件失败:', error);
    return false;
  }
}

// 发送密码重置邮件
export async function sendPasswordReset(email: string, token: string, username: string): Promise<boolean> {
  try {
    const baseUrl = process.env.NUXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    const resetUrl = `${baseUrl}/auth/reset-password?token=${token}&email=${encodeURIComponent(email)}`;

    const content = `
      <p>您好，<strong>${username}</strong>！</p>
      <p>我们收到了您的密码重置请求。如果这不是您本人的操作，请忽略此邮件。</p>
      <p>要重置您的密码，请点击下面的按钮：</p>
      <div class="divider"></div>
      <p><strong>安全提示：</strong></p>
      <ul>
        <li>此重置链接将在1小时后过期</li>
        <li>重置链接只能使用一次</li>
        <li>请选择一个强密码来保护您的账户</li>
        <li>如果您没有请求密码重置，请立即联系我们</li>
      </ul>
    `;

    const emailOptions: EmailOptions = {
      to: email,
      subject: 'AI Game Platform - 密码重置',
      html: generateEmailTemplate(
        '密码重置',
        content,
        resetUrl,
        '重置密码'
      )
    };

    const success = await sendEmail(emailOptions);
    if (success) {
      console.log(`密码重置邮件已发送: ${email} 用户: ${username}`);
    }
    return success;
  } catch (error) {
    console.error('发送密码重置邮件失败:', error);
    return false;
  }
}

// 导出配置获取函数，供其他模块使用
export { getSMTPConfig };
