import { useAuth } from '../../context/AuthContext'
import { useStudentDashboard, useMyTrends } from '../../hooks'
import { Card, PageHeader, RiskBadge, QueryState } from '../../components/ui'
import { MultiLineChart } from '../../components/charts'

export default function ProfilePage() {
  const { user } = useAuth()
  const { data: dashboard, isLoading, error, refetch } = useStudentDashboard()
  const { data: trends } = useMyTrends()

  return (
    <div>
      <PageHeader title="Profile" subtitle={user?.full_name} />
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Account">
            <dl className="space-y-2 text-sm">
              <div><dt className="text-slate-500">Email</dt><dd>{user?.email}</dd></div>
              <div><dt className="text-slate-500">Entity ID</dt><dd>{user?.entity_id}</dd></div>
              <div><dt className="text-slate-500">Risk Status</dt><dd className="mt-1"><RiskBadge risk={dashboard?.overview?.risk?.overall} /></dd></div>
            </dl>
          </Card>
          <Card title="Performance Overview">
            <dl className="space-y-2 text-sm">
              <div><dt className="text-slate-500">Questions Solved</dt><dd>{dashboard?.question_stats?.questions_solved}</dd></div>
              <div><dt className="text-slate-500">Total Points</dt><dd>{dashboard?.question_stats?.total_points}</dd></div>
              <div><dt className="text-slate-500">Avg Rank</dt><dd>{dashboard?.question_stats?.avg_approved_rank ?? '—'}</dd></div>
              <div><dt className="text-slate-500">Leaderboard Position</dt><dd>{dashboard?.overview?.leaderboard_position ?? '—'}</dd></div>
            </dl>
          </Card>
          {trends && (
            <Card title="Performance Trends" className="lg:col-span-2">
              <MultiLineChart
                data={trends.attendance_trend?.map((d, i) => ({
                  day: d.day,
                  attendance: trends.attendance_trend[i]?.value,
                  assignment: trends.assignment_trend[i]?.value,
                  test: trends.test_trend[i]?.value,
                  question: trends.question_performance_trend[i]?.value,
                }))}
                lines={[
                  { key: 'attendance', name: 'Attendance' },
                  { key: 'assignment', name: 'Assignment' },
                  { key: 'test', name: 'Test' },
                  { key: 'question', name: 'Questions' },
                ]}
              />
            </Card>
          )}
        </div>
      </QueryState>
    </div>
  )
}
