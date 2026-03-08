import type { SafeUser } from '~/server/utils/auth'

interface AuthState {
  user: SafeUser | null
  isLoggedIn: boolean
  isLoading: boolean
}

function createAuthError(error: any, fallbackMessage: string) {
  const payload = error?.data ?? error?.response?._data

  return createError({
    statusCode: error?.status ?? error?.statusCode ?? error?.response?.status ?? payload?.statusCode ?? 400,
    statusMessage: payload?.statusMessage ?? payload?.message ?? error?.statusMessage ?? error?.message ?? fallbackMessage
  })
}

export const useCustomAuth = () => {
  const user = useState<SafeUser | null>('auth.user', () => null)
  const isLoading = useState<boolean>('auth.loading', () => false)

  const isLoggedIn = computed(() => !!user.value)
  const requestFetch = process.server ? useRequestFetch() : $fetch

  const login = async (identifier: string, password: string) => {
    isLoading.value = true
    try {
      const data = await requestFetch<{ success: boolean; user: SafeUser; token: string }>('/api/auth/login', {
        method: 'POST',
        body: { identifier, password },
        credentials: 'include'
      })

      if (data.success) {
        user.value = data.user
        await navigateTo('/')
      }

      return { success: true }
    } catch (error: any) {
      throw createAuthError(error, 'Login failed')
    } finally {
      isLoading.value = false
    }
  }

  const register = async (username: string, email: string, password: string, phoneNumber?: string, studentId?: string, realName?: string, education?: string) => {
    isLoading.value = true
    try {
      const body = {
        username,
        email,
        password,
        ...(phoneNumber ? { phoneNumber } : {}),
        ...(studentId ? { studentId } : {}),
        ...(realName ? { realName } : {}),
        ...(education ? { education } : {})
      }

      const data = await requestFetch<{ success: boolean; user: SafeUser; token: string }>('/api/auth/register', {
        method: 'POST',
        body,
        credentials: 'include'
      })

      if (data.success) {
        user.value = data.user
        await navigateTo('/')
      }

      return { success: true }
    } catch (error: any) {
      throw createAuthError(error, 'Registration failed')
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    isLoading.value = true
    try {
      await requestFetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      })

      user.value = null
      await navigateTo('/login')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      isLoading.value = false
    }
  }

  const fetchUser = async () => {
    isLoading.value = true
    try {
      const data = await requestFetch<{ success: boolean; user: SafeUser }>('/api/auth/me', {
        credentials: 'include'
      })

      if (data.success) {
        user.value = data.user
      }
    } catch (error) {
      user.value = null
    } finally {
      isLoading.value = false
    }
  }

  return {
    user: readonly(user),
    isLoggedIn,
    isLoading: readonly(isLoading),
    login,
    register,
    logout,
    fetchUser
  }
}

// 创建别名以便在中间件中使用
export const useAuth = useCustomAuth
