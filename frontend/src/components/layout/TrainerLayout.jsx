import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useEntity } from '../../context/EntityContext'
import { Select, Button, Loading } from '../ui'

const navItems = (entityId) => [
  { to: '/trainer/dashboard', label: 'Dashboard', end: true },
  { to: '/trainer/entities', label: 'Entities' },
  ...(entityId
    ? [
        { to: `/trainer/entities/${entityId}/subjects`, label: 'Subjects' },
        { to: `/trainer/entities/${entityId}/students`, label: 'Students' },
        { to: `/trainer/entities/${entityId}/attendance`, label: 'Attendance' },
        { to: `/trainer/entities/${entityId}/assignments`, label: 'Assignments' },
        { to: `/trainer/entities/${entityId}/presentations`, label: 'Presentations' },
        { to: `/trainer/entities/${entityId}/test-scores`, label: 'Test Scores' },
        { to: `/trainer/entities/${entityId}/daily-notes`, label: 'Daily Notes' },
        { to: `/trainer/entities/${entityId}/questions`, label: 'Questions' },
        { to: '/trainer/questions/active', label: 'Active Question' },
        { to: '/trainer/questions/verification', label: 'Verification' },
        { to: `/trainer/entities/${entityId}/question-statistics`, label: 'Question Stats' },
        { to: `/trainer/entities/${entityId}/leaderboard`, label: 'Leaderboard' },
        { to: `/trainer/entities/${entityId}/analytics`, label: 'Analytics' },
        { to: `/trainer/entities/${entityId}/daily-summary`, label: 'Daily Summary' },
        { to: `/trainer/entities/${entityId}/import-export`, label: 'Import/Export' },
      ]
    : []),
]

export default function TrainerLayout() {
  const { user, logout } = useAuth()
  const { entityId, setEntityId, entities, isLoading } = useEntity()
  const navigate = useNavigate()

  if (isLoading) return <Loading />

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="fixed flex h-full w-60 flex-col border-r border-slate-200 bg-white">
        <div className="border-b border-slate-100 px-4 py-5">
          <h1 className="text-lg font-bold text-primary-700">Fabricator</h1>
          <p className="text-xs text-slate-500">Trainer Portal</p>
        </div>
        {entities.length > 0 && (
          <div className="border-b border-slate-100 px-3 py-3">
            <Select
              label="Workshop"
              value={entityId || ''}
              onChange={(e) => setEntityId(Number(e.target.value))}
              options={entities.map((e) => ({ value: e.id, label: e.name }))}
            />
          </div>
        )}
        <nav className="flex-1 overflow-y-auto px-2 py-3">
          {navItems(entityId).map((item) => (
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
          <p className="truncate text-xs text-slate-500">{user?.email}</p>
          <Button variant="ghost" className="mt-2 w-full text-left" onClick={() => { logout(); navigate('/login') }}>
            Logout
          </Button>
        </div>
      </aside>
      <main className="ml-60 flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}
