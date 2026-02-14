import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiRequest } from '../lib/api'
import type { Post } from '../types'

function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void (async () => {
      try {
        const data = await apiRequest<Post[]>('/api/posts/')
        setPosts(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load posts')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) {
    return <p>Loading posts…</p>
  }

  if (error) {
    return <p className="text-red-600">{error}</p>
  }

  return (
    <section>
      <div className="mb-5 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Posts</h1>
        <Link to="/posts/new" className="rounded bg-slate-900 px-3 py-2 text-sm text-white">Create Post</Link>
      </div>

      {posts.length === 0 ? (
        <p className="rounded border bg-white p-4 text-slate-600">No posts yet.</p>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {posts.map((post) => (
            <li key={post.id} className="rounded-xl border bg-white p-4 shadow-sm">
              <h2 className="text-lg font-semibold">
                <Link className="hover:underline" to={`/posts/${post.id.split('-')[0]}-${post.slug}`}>{post.title}</Link>
              </h2>
              <p className="mt-1 text-sm text-slate-500">/{post.slug}</p>
              <p className="mt-3 text-sm text-slate-700 line-clamp-3">{post.summary || 'No summary provided.'}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default PostsPage
