import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Button } from '../ui'

const navItems = [
  { to: '/student/dashboard', label: 'Dashboard', end: true },
  { to: '/student/active-question', label: 'Active Question' },
  { to: '/student/question-history', label: 'Question History' },
  { to: '/student/leaderboard', label: 'Leaderboard' },
  { to: '/student/profile', label: 'Profile' },
]

export default function StudentLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="fixed flex h-full w-56 flex-col border-r border-slate-200 bg-white">
        <div className="border-b border-slate-100 px-4 py-5">
          <h1 className="text-lg font-bold text-primary-700">Fabricator</h1>
          <p className="text-xs text-slate-500">Student Portal</p>
        </div>
        <nav className="flex-1 px-2 py-3">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `mb-0.5 block rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-100'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-100 p-4">
          <p className="truncate text-sm font-medium">{user?.full_name}</p>
          <Button variant="ghost" className="mt-2 w-full text-left" onClick={() => { logout(); navigate('/login') }}>
            Logout
          </Button>
        </div>
      </aside>
      <main className="ml-56 flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}
