import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { apiRequest } from '../lib/api'
import type { Post } from '../types'

type Props = {
  mode: 'create' | 'edit'
  userId: string
}

function PostEditorPage({ mode, userId }: Props) {
  const navigate = useNavigate()
  const { postId, display } = useParams()

  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [contentHtml, setContentHtml] = useState('')
  const [status, setStatus] = useState<'draft' | 'published'>('published')
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(mode === 'edit')
  const [error, setError] = useState<string | null>(null)
  const [loadedPost, setLoadedPost] = useState<Post | null>(null)

  // Get access token from localStorage (or your auth context)
  const token = localStorage.getItem('blog_access_token')

  useEffect(() => {
    if (mode !== 'edit') {
      return
    }

    const loadByShort = async (shortId: string) => {
      try {
        const post = await apiRequest<Post>(`/api/posts/short/${shortId}`)
        setLoadedPost(post)
        setTitle(post.title)
        setSummary(post.summary ?? '')
        setContentHtml(post.content_html ?? '')
        setStatus(post.status === 'published' ? 'published' : 'draft')
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load post')
      } finally {
        setFetching(false)
      }
    }

    if (postId) {
      void (async () => {
        try {
          const post = await apiRequest<Post>(`/api/posts/${postId}`)
          setLoadedPost(post)
          setTitle(post.title)
          setSummary(post.summary ?? '')
          setContentHtml(post.content_html ?? '')
          setStatus(post.status === 'published' ? 'published' : 'draft')
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to load post')
        } finally {
          setFetching(false)
        }
      })()
      return
    }

    if (display && display.includes('-')) {
      const [shortId] = display.split('-')
      void loadByShort(shortId)
      return
    }

    setError('Missing post id')
    setFetching(false)
  }, [mode, postId, display])

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)

    const payload = {
      author_id: userId,
      title,
      status,
      summary: summary || null,
      content_html: contentHtml || null,
      published_at: status === 'published' ? new Date().toISOString() : null,
    }

    try {
      if (mode === 'create') {
        const created = await apiRequest<Post>('/api/posts/', { method: 'POST', body: payload, token })
        navigate(`/posts/${created.id.split('-')[0]}-${created.slug}`)
      } else {
        const idToUse = postId ?? loadedPost?.id
        if (!idToUse) {
          throw new Error('Missing post id')
        }

        const updated = await apiRequest<Post>(`/api/posts/${idToUse}`, { method: 'PUT', body: payload, token })
        navigate(`/posts/${updated.id.split('-')[0]}-${updated.slug}`)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save post'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return <p>Loading editor…</p>
  }

  return (
    <section className="rounded-xl border bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold">{mode === 'create' ? 'Create Post' : 'Edit Post'}</h1>

      <form onSubmit={onSubmit} className="mt-5 space-y-4">
        <label className="block">
          <span className="mb-1 block text-sm font-medium">Title</span>
          <input
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium">Summary</span>
          <textarea
            rows={3}
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium">Content</span>
          <textarea
            rows={8}
            value={contentHtml}
            onChange={(e) => setContentHtml(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium">Status</span>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as 'draft' | 'published')}
            className="w-full rounded border px-3 py-2"
          >
            <option value="published">Published</option>
            <option value="draft">Draft</option>
          </select>
        </label>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="flex items-center gap-3">
          <button disabled={loading} type="submit" className="rounded bg-slate-900 px-4 py-2 text-white disabled:opacity-60">
            {loading ? 'Saving…' : mode === 'create' ? 'Create post' : 'Update post'}
          </button>
          <Link className="rounded border px-4 py-2" to="/posts">Cancel</Link>
        </div>
      </form>
    </section>
  )
}

export default PostEditorPage
