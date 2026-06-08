import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useSubjects, useLeaderboard } from '../../hooks'
import { Card, PageHeader, Select, DataTable, QueryState, RiskBadge } from '../../components/ui'

function RankDisplay({ rank }) {
  if (rank === 1) return <span className="font-bold text-amber-600">🥇 {rank}</span>
  if (rank === 2) return <span className="font-bold text-slate-500">🥈 {rank}</span>
  if (rank === 3) return <span className="font-bold text-amber-800">🥉 {rank}</span>
  return rank ?? '—'
}

export default function LeaderboardPage() {
  const { id: entityId } = useParams()
  const [subjectId, setSubjectId] = useState('all')

  const { data: subjects = [] } = useSubjects(entityId)
  const { data: board = [], isLoading, error, refetch } = useLeaderboard(entityId, subjectId)

  const ranked = board.filter((e) => e.rank != null)

  return (
    <div>
      <PageHeader title="Leaderboard" subtitle={`${ranked.length} ranked students`} action={
        <Select
          value={subjectId}
          onChange={(e) => setSubjectId(e.target.value)}
          options={[{ value: 'all', label: 'All Subjects' }, ...subjects.map((s) => ({ value: s.id, label: s.name }))]}
          className="w-48"
        />
      } />
      <Card>
        <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
          <DataTable
            columns={[
              { key: 'rank', label: 'Rank', render: (r) => <RankDisplay rank={r.rank} /> },
              {
                key: 'student_name',
                label: 'Student',
                render: (r) => (
                  <Link to={`/trainer/entities/${entityId}/students/${r.student_id}`} className="text-primary-600 hover:underline">
                    {r.student_name}
                  </Link>
                ),
              },
              { key: 'avg_approved_rank', label: 'Avg Rank', render: (r) => r.avg_approved_rank ?? '—' },
              { key: 'total_points', label: 'Total Points' },
              { key: 'avg_completion_time_seconds', label: 'Avg Time (s)', render: (r) => r.avg_completion_time_seconds ?? '—' },
              { key: 'risk', label: 'Risk', render: (r) => <RiskBadge risk={r.risk} /> },
            ]}
            data={board}
            keyField="student_id"
          />
        </QueryState>
      </Card>
    </div>
  )
}
