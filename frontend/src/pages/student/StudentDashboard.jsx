import { useAuth } from '../../context/AuthContext'
import { useStudentDashboard } from '../../hooks'
import { Card, StatCard, PageHeader, RiskBadge, Badge, QueryState } from '../../components/ui'
import { TrendLineChart } from '../../components/charts'

export default function StudentDashboard() {
  const { user } = useAuth()
  const { data, isLoading, error, refetch } = useStudentDashboard()

  const o = data?.overview || {}
  const qs = data?.question_stats || {}

  return (
    <div>
      <PageHeader title="Dashboard" subtitle={`Welcome, ${user?.full_name || user?.email}`} />
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3">
          <StatCard label="Attendance" value={o.attendance_pct != null ? `${o.attendance_pct}%` : '—'} color="green" />
          <StatCard label="Assignments" value={o.assignment_pct != null ? `${o.assignment_pct}%` : '—'} />
          <StatCard label="Avg Presentation" value={o.avg_presentation_score ?? '—'} />
          <StatCard label="Avg Test Score" value={o.avg_test_score ?? '—'} />
          <StatCard label="Leaderboard #" value={o.leaderboard_position ?? '—'} color="blue" />
          <div className="rounded-xl bg-slate-100 p-4">
            <p className="text-xs font-medium uppercase text-slate-500">Risk</p>
            <div className="mt-2"><RiskBadge risk={o.risk?.overall} /></div>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard label="Questions Solved" value={qs.questions_solved} />
          <StatCard label="Avg Rank" value={qs.avg_approved_rank ?? '—'} />
          <StatCard label="Total Points" value={qs.total_points} color="blue" />
          <StatCard label="Avg Completion" value={qs.avg_completion_time_seconds != null ? `${qs.avg_completion_time_seconds}s` : '—'} />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Attendance Trend">
            <TrendLineChart data={data?.performance_trends?.attendance_trend?.filter((d) => d.value != null)} color="#10b981" />
          </Card>
          <Card title="Question Performance">
            <TrendLineChart data={data?.performance_trends?.question_performance_trend?.filter((d) => d.value != null)} color="#f59e0b" />
          </Card>
        </div>

        {o.risk?.dimensions && (
          <Card title="Risk Breakdown" className="mt-6">
            <div className="flex flex-wrap gap-3">
              {Object.entries(o.risk.dimensions).map(([k, v]) => (
                <Badge key={k} color={v === 'green' ? 'green' : v === 'yellow' ? 'yellow' : 'red'}>
                  {k}: {v}
                </Badge>
              ))}
            </div>
          </Card>
        )}
      </QueryState>
    </div>
  )
}
