import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { useSubjects, useStudentLeaderboard } from '../../hooks'
import { Card, PageHeader, Select, DataTable, QueryState } from '../../components/ui'

function RankDisplay({ rank, highlight }) {
  const cls = highlight ? 'font-bold text-primary-600' : ''
  if (rank === 1) return <span className={`font-bold text-amber-600 ${cls}`}>🥇 {rank}</span>
  if (rank === 2) return <span className={`font-bold text-slate-500 ${cls}`}>🥈 {rank}</span>
  if (rank === 3) return <span className={`font-bold text-amber-800 ${cls}`}>🥉 {rank}</span>
  return <span className={cls}>{rank ?? '—'}</span>
}

export default function StudentLeaderboardPage() {
  const { user } = useAuth()
  const [subjectId, setSubjectId] = useState('all')
  const entityId = user?.entity_id

  const { data: subjects = [] } = useSubjects(entityId, { enabled: !!entityId })
  const { data: board = [], isLoading, error, refetch } = useStudentLeaderboard(entityId, subjectId)

  return (
    <div>
      <PageHeader title="Leaderboard" action={
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
              {
                key: 'rank',
                label: 'Rank',
                render: (r) => (
                  <RankDisplay rank={r.rank} highlight={r.student_id === user?.student_id} />
                ),
              },
              {
                key: 'student_name',
                label: 'Student',
                render: (r) => (
                  <span className={r.student_id === user?.student_id ? 'font-bold text-primary-600' : ''}>
                    {r.student_name}
                    {r.student_id === user?.student_id && ' (You)'}
                  </span>
                ),
              },
              { key: 'avg_approved_rank', label: 'Avg Rank', render: (r) => r.avg_approved_rank ?? '—' },
              { key: 'total_points', label: 'Points' },
              { key: 'avg_completion_time_seconds', label: 'Avg Time (s)', render: (r) => r.avg_completion_time_seconds ?? '—' },
            ]}
            data={board}
            keyField="student_id"
          />
        </QueryState>
      </Card>
    </div>
  )
}
