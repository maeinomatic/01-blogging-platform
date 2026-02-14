export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:5000'

type RequestOptions = {
  method?: string
  token?: string | null
  body?: unknown
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const json = await response.json()
      if (json?.detail) {
        message = String(json.detail)
      }
    } catch {
   
    throw new Error(message)
  }
 }
  return response.json() as Promise<T>
}
