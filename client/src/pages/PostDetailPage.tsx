import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { apiRequest } from '../lib/api'
import type { Post } from '../types'

type Props = {
  userId: string | null
}

function PostDetailPage({ userId }: Props) {
  const navigate = useNavigate()
  const { postId, slug, display } = useParams()
  const [post, setPost] = useState<Post | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const shortIdLookup = async (shortId: string, slugFromUrl?: string) => {
      try {
        const data = await apiRequest<Post>(`/api/posts/short/${shortId}`)
        setPost(data)
        if (slugFromUrl && data.slug !== slugFromUrl) {
          navigate(`/posts/${data.id.split('-')[0]}-${data.slug}`, { replace: true })
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load post')
      } finally {
        setLoading(false)
      }
    }

    if (postId) {
      void (async () => {
        try {
          const data = await apiRequest<Post>(`/api/posts/${postId}`)
          setPost(data)
          if (slug && slug !== data.slug) {
            navigate(`/posts/${data.id.split('-')[0]}-${data.slug}`, { replace: true })
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to load post')
        } finally {
          setLoading(false)
        }
      })()
      return
    }

    if (!display) {
      setError('Missing post id')
      setLoading(false)
      return
    }

    if (display.includes('-')) {
      const [shortId, ...slugParts] = display.split('-')
      const slugFromUrl = slugParts.join('-')
      void shortIdLookup(shortId, slugFromUrl)
      return
    }

    // fallback: treat display as full id
    void (async () => {
      try {
        const data = await apiRequest<Post>(`/api/posts/${display}`)
        setPost(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load post')
      } finally {
        setLoading(false)
      }
    })()
  }, [postId, display, slug, navigate])

  if (loading) {
    return <p>Loading post…</p>
  }

  if (error || !post) {
    return <p className="text-red-600">{error || 'Post not found'}</p>
  }

  return (
    <article className="rounded-xl border bg-white p-6 shadow-sm">
      <p className="text-sm text-slate-500">/{post.slug}</p>
      <h1 className="mt-1 text-3xl font-bold">{post.title}</h1>
      {post.summary && <p className="mt-3 text-slate-700">{post.summary}</p>}

      <div className="mt-6 rounded border bg-slate-50 p-4 text-sm leading-6 text-slate-800">
        {post.content_html || 'No content available.'}
      </div>

      <div className="mt-6 flex items-center gap-3">
        <Link className="rounded border px-3 py-1.5" to="/posts">Back</Link>
        {userId === post.author_id && (
          <Link className="rounded bg-slate-900 px-3 py-1.5 text-white" to={`/posts/${post.id.split('-')[0]}-${post.slug}/edit`}>
            Edit post
          </Link>
        )}
      </div>
    </article>
  )
}

export default PostDetailPage
