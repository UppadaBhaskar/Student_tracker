import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { getErrorMessage } from '../../api/errors'
import { Button, Input, Card, Alert } from '../../components/ui'

export default function LoginPage() {
  const { login, isLoggingIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const user = await login(email, password)
      navigate(user.role === 'trainer' ? '/trainer/dashboard' : '/student/dashboard')
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-100 to-blue-50 p-4">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-slate-900">Fabricator</h1>
          <p className="text-sm text-slate-500">Workshop Performance Tracker</p>
        </div>
        {error && <Alert className="mb-4">{error}</Alert>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button type="submit" className="w-full" disabled={isLoggingIn}>
            {isLoggingIn ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
        <p className="mt-4 text-center text-xs text-slate-400">
          Demo: trainer@workshop.local / trainer123
        </p>
      </Card>
    </div>
  )
}
