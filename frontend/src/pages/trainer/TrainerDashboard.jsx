import { Link } from 'react-router-dom'
import { useParams } from 'react-router-dom'
import { useEntity } from '../../context/EntityContext'
import { useTrainerDashboard } from '../../hooks'
import { Card, StatCard, PageHeader, DataTable, Badge, QueryState, RiskBadge } from '../../components/ui'
import { TrendLineChart, RiskPieChart, ParticipationChart } from '../../components/charts'

export default function TrainerDashboard() {
  const { entityId, entity } = useEntity()
  const { data, isLoading, error, refetch } = useTrainerDashboard(entityId)

  if (!entityId) {
    return (
      <div>
        <PageHeader title="Dashboard" subtitle="Select or create a workshop entity" />
        <Card>
          <p className="text-slate-600">No entity selected. <Link to="/trainer/entities" className="text-primary-600">Manage entities</Link></p>
        </Card>
      </div>
    )
  }

  const s = data?.today_summary || {}
  const participation = data?.question_participation_today

  return (
    <div>
      <PageHeader title="Dashboard" subtitle={entity?.name} />
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard label="Day" value={s.current_day} />
          <StatCard label="Total Students" value={s.total_students} />
          <StatCard label="Present Today" value={s.present_today} color="green" />
          <StatCard label="Attendance %" value={`${s.attendance_pct}%`} />
          <StatCard label="Assignment %" value={`${s.assignment_completion_pct}%`} />
          <StatCard label="Avg Test Score" value={s.avg_test_score ?? '—'} />
          <StatCard label="Pending Verifications" value={s.pending_verifications} color="yellow" />
          <StatCard label="At-Risk Students" value={s.risk_students_count} color="red" />
        </div>

        <div className="mb-6 grid gap-6 lg:grid-cols-3">
          <Card title="Attendance Trend">
            <TrendLineChart data={data?.attendance_trend} color="#10b981" />
          </Card>
          <Card title="Question Performance">
            <TrendLineChart data={data?.question_performance_trend} color="#f59e0b" />
          </Card>
          <Card title="Risk Distribution">
            <RiskPieChart data={data?.risk_distribution} />
            {data?.risk_distribution && (
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                <Badge color="green">Green: {data.risk_distribution.green}</Badge>
                <Badge color="yellow">Yellow: {data.risk_distribution.yellow}</Badge>
                <Badge color="red">Red: {data.risk_distribution.red}</Badge>
              </div>
            )}
          </Card>
        </div>

        {participation && (
          <Card title={`Question Participation (Day ${s.current_day})`} className="mb-6">
            <ParticipationChart data={[participation]} />
          </Card>
        )}

        <div className="mb-6 grid gap-6 lg:grid-cols-2">
          <Card title="Top 5 Students">
            <DataTable
              columns={[
                { key: 'rank', label: '#', render: (r) => r.rank ?? '—' },
                { key: 'student_name', label: 'Name' },
                { key: 'avg_approved_rank', label: 'Avg Rank' },
                { key: 'total_points', label: 'Points' },
              ]}
              data={data?.top_5_students || []}
              keyField="student_id"
            />
          </Card>
          <Card title="Bottom 5 Students">
            <DataTable
              columns={[
                { key: 'rank', label: '#', render: (r) => r.rank ?? '—' },
                { key: 'student_name', label: 'Name' },
                { key: 'avg_approved_rank', label: 'Avg Rank' },
                { key: 'total_points', label: 'Points' },
              ]}
              data={data?.bottom_5_students || []}
              keyField="student_id"
            />
          </Card>
        </div>

        <Card title="At-Risk Students" className="mb-6">
          {(data?.at_risk_students || []).length === 0 ? (
            <p className="text-sm text-slate-500">No students currently flagged yellow or red.</p>
          ) : (
            <DataTable
              columns={[
                { key: 'usn', label: 'USN' },
                { key: 'student_name', label: 'Name' },
                { key: 'overall', label: 'Risk', render: (r) => <RiskBadge risk={r.overall} /> },
                {
                  key: 'metrics',
                  label: 'Attendance',
                  render: (r) => (r.metrics?.attendance_pct != null ? `${r.metrics.attendance_pct}%` : '—'),
                },
                {
                  key: 'assignments',
                  label: 'Assignments',
                  render: (r) => (r.metrics?.assignment_pct != null ? `${r.metrics.assignment_pct}%` : '—'),
                },
                {
                  key: 'actions',
                  label: '',
                  render: (r) => (
                    <Link to={`/trainer/entities/${entityId}/students/${r.student_id}`} className="text-primary-600 text-sm">
                      View
                    </Link>
                  ),
                },
              ]}
              data={data.at_risk_students}
              keyField="student_id"
            />
          )}
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Top Subject">
            {data?.top_subject ? (
              <div className="space-y-2 text-sm">
                <p className="text-lg font-semibold">{data.top_subject.subject_name}</p>
                <p>Avg Points: {data.top_subject.avg_points ?? '—'}</p>
                <p>Completion: {data.top_subject.completion_rate}%</p>
                <Badge color="green">Score: {data.top_subject.difficulty_score}</Badge>
              </div>
            ) : (
              <p className="text-slate-500">No data</p>
            )}
          </Card>
          <Card title="Weakest Subject">
            {data?.weakest_subject ? (
              <div className="space-y-2 text-sm">
                <p className="text-lg font-semibold">{data.weakest_subject.subject_name}</p>
                <p>Avg Points: {data.weakest_subject.avg_points ?? '—'}</p>
                <p>Completion: {data.weakest_subject.completion_rate}%</p>
                <Badge color="red">Score: {data.weakest_subject.difficulty_score}</Badge>
              </div>
            ) : (
              <p className="text-slate-500">No data</p>
            )}
          </Card>
          <Card title="Active Question" className="lg:col-span-2">
            {s.active_question ? (
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">{s.active_question.title}</p>
                  <p className="text-sm text-slate-500">{s.active_question.subject}</p>
                </div>
                <Link to="/trainer/questions/active" className="text-sm text-primary-600">View →</Link>
              </div>
            ) : (
              <p className="text-slate-500">No active question</p>
            )}
          </Card>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/trainer/questions/verification" className="rounded-lg bg-primary-600 px-4 py-2 text-sm text-white">
            Verification Queue ({s.pending_verifications || 0})
          </Link>
          <Link to={`/trainer/entities/${entityId}/attendance`} className="rounded-lg border px-4 py-2 text-sm">
            Today's Attendance
          </Link>
          <Link to={`/trainer/entities/${entityId}/analytics`} className="rounded-lg border px-4 py-2 text-sm">
            Full Analytics
          </Link>
          <Link to={`/trainer/entities/${entityId}/leaderboard`} className="rounded-lg border px-4 py-2 text-sm">
            Leaderboard
          </Link>
        </div>
      </QueryState>
    </div>
  )
}
