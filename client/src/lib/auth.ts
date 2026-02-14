type AuthState = {
  accessToken: string | null
  refreshToken: string | null
  userId: string | null
}

const ACCESS_TOKEN_KEY = 'blog_access_token'
const REFRESH_TOKEN_KEY = 'blog_refresh_token'

function parseTokenSub(token: string): string | null {
  try {
    const payload = token.split('.')[1]
    if (!payload) {
      return null
    }
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return decoded?.sub ?? null
  } catch {
    return null
  }
}

export function getStoredAuth(): AuthState {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
  const userId = accessToken ? parseTokenSub(accessToken) : null

  return {
    accessToken,
    refreshToken,
    userId,
  }
}

export function saveTokens(accessToken: string, refreshToken: string): AuthState {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  return getStoredAuth()
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}
