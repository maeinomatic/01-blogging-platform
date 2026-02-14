import { Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { useMemo, useState } from 'react'
import { clearTokens, getStoredAuth, saveTokens } from './lib/auth'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import PostsPage from './pages/PostsPage'
import PostDetailPage from './pages/PostDetailPage'
import PostEditorPage from './pages/PostEditorPage'
import { apiRequest } from './lib/api'

function App() {
  const navigate = useNavigate()
  const [auth, setAuth] = useState(getStoredAuth())

  const isAuthed = useMemo(() => Boolean(auth.accessToken && auth.userId), [auth])

  const onLogin = (accessToken: string, refreshToken: string) => {
    const next = saveTokens(accessToken, refreshToken)
    setAuth(next)
    navigate('/posts')
  }

  const onLogout = async () => {
    if (auth.refreshToken) {
      try {
        await apiRequest('/api/auth/logout', {
          method: 'POST',
          body: { refresh_token: auth.refreshToken },
        })
      } catch {
      }
    }
    clearTokens()
    setAuth(getStoredAuth())
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <nav className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-3">
          <Link to="/posts" className="text-lg font-semibold">Blogging Platform</Link>
          <div className="flex items-center gap-3 text-sm">
            <Link to="/posts" className="hover:underline">Posts</Link>
            {!isAuthed ? (
              <>
                <Link to="/login" className="hover:underline">Login</Link>
                <Link to="/register" className="hover:underline">Register</Link>
              </>
            ) : (
              <>
                <Link to="/posts/new" className="rounded bg-slate-900 px-3 py-1.5 text-white">New Post</Link>
                <button onClick={onLogout} className="rounded border px-3 py-1.5">Logout</button>
              </>
            )}
          </div>
        </nav>
      </header>

      <main className="mx-auto w-full max-w-5xl px-4 py-6">
        <Routes>
          <Route path="/" element={<Navigate to="/posts" replace />} />
          <Route path="/login" element={<LoginPage onLogin={onLogin} />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/posts" element={<PostsPage />} />
          <Route path="/posts/:display" element={<PostDetailPage userId={auth.userId} />} />
          <Route path="/posts/:postId" element={<PostDetailPage userId={auth.userId} />} />
          <Route path="/posts/:postId/:slug" element={<PostDetailPage userId={auth.userId} />} />
          <Route
            path="/posts/new"
            element={isAuthed ? <PostEditorPage mode="create" userId={auth.userId!} /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/posts/:display/edit"
            element={isAuthed ? <PostEditorPage mode="edit" userId={auth.userId!} /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/posts/:postId/:slug/edit"
            element={isAuthed ? <PostEditorPage mode="edit" userId={auth.userId!} /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/posts/:postId/edit"
            element={isAuthed ? <PostEditorPage mode="edit" userId={auth.userId!} /> : <Navigate to="/login" replace />}
          />
        </Routes>
      </main>
    </div>
  )
}

export default App
