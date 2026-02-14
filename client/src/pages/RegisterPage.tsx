import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiRequest } from '../lib/api'

function RegisterPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await apiRequest('/api/auth/register', {
        method: 'POST',
        body: { email, username, password },
      })
      navigate('/login')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="mx-auto w-full max-w-md rounded-xl border bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold">Register</h1>
      <p className="mt-1 text-sm text-slate-600">Create an account to start posting.</p>

      <form onSubmit={onSubmit} className="mt-5 space-y-4">
        <label className="block">
          <span className="mb-1 block text-sm font-medium">Email</span>
          <input
            required
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium">Username</span>
          <input
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium">Password</span>
          <input
            required
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </label>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          disabled={loading}
          type="submit"
          className="w-full rounded bg-slate-900 px-4 py-2 text-white disabled:opacity-60"
        >
          {loading ? 'Creating account…' : 'Register'}
        </button>
      </form>

      <p className="mt-4 text-sm text-slate-600">
        Already registered? <Link className="underline" to="/login">Login</Link>
      </p>
    </section>
  )
}

export default RegisterPage
