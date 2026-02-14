export type AuthLoginResponse = {
  access_token: string
  refresh_token: string
  token_type: string
}

export type Post = {
  id: string
  author_id: string
  title: string
  slug: string
  status: string
  published_at: string | null
  summary: string | null
  content_html: string | null
  comments_count: number
  likes_count: number
  created_at: string
  updated_at: string | null
}
