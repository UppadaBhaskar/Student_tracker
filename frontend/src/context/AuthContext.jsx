import { createContext, useContext, useEffect, useState } from 'react'
import { useAuthSession, useLoginMutation, useLogout } from '../hooks/useAuth'
import { getErrorMessage } from '../api/errors'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user') || 'null')
    } catch {
      return null
    }
  })

  const hasToken = !!localStorage.getItem('token')
  const sessionQuery = useAuthSession(hasToken)
  const loginMutation = useLoginMutation()
  const logoutFn = useLogout()

  useEffect(() => {
    if (sessionQuery.data) {
      setUser(sessionQuery.data)
      localStorage.setItem('user', JSON.stringify(sessionQuery.data))
    }
  }, [sessionQuery.data])

  useEffect(() => {
    if (sessionQuery.isError && hasToken) {
      logoutFn()
      setUser(null)
    }
  }, [sessionQuery.isError, hasToken, logoutFn])

  const loading = hasToken && sessionQuery.isLoading

  const login = async (email, password) => {
    const data = await loginMutation.mutateAsync({ email, password })
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    logoutFn()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isTrainer: user?.role === 'trainer',
        loginError: loginMutation.error ? getErrorMessage(loginMutation.error) : null,
        isLoggingIn: loginMutation.isPending,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
