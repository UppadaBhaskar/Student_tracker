import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Loading } from '../ui'

export function ProtectedRoute({ role }) {
  const { user, loading } = useAuth()
  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role) {
    return <Navigate to={user.role === 'trainer' ? '/trainer/dashboard' : '/student/dashboard'} replace />
  }
  return <Outlet />
}
