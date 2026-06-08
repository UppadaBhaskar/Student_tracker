import { useState } from 'react'
import { useQuestionHistory } from '../../hooks'
import { Card, PageHeader, Badge, DataTable, QueryState } from '../../components/ui'

export default function QuestionHistoryPage() {
  const [expanded, setExpanded] = useState(null)
  const { data: history = [], isLoading, error, refetch } = useQuestionHistory()

  return (
    <div>
      <PageHeader title="Question History" />
      <QueryState
        isLoading={isLoading}
        error={error}
        isEmpty={!history.length}
        emptyMessage="No question history yet"
        onRetry={refetch}
      >
        <div className="space-y-4">
          {history.map((item) => (
            <Card key={item.question_id}>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold">{item.title}</h3>
                  <p className="text-sm text-slate-500">{item.subject} · Day {item.day}</p>
                </div>
                <div className="flex gap-2">
                  <Badge color={item.final_status === 'approved' ? 'green' : item.final_status === 'rejected' ? 'red' : 'yellow'}>
                    {item.final_status}
                  </Badge>
                  {item.approved_rank && <Badge color="blue">Rank {item.approved_rank}</Badge>}
                  {item.points != null && <Badge>{item.points} pts</Badge>}
                </div>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-4 text-sm text-slate-600">
                <span>Attempts: {item.attempt_count}</span>
                <span>Points: {item.points ?? '—'}</span>
                <span>Time: {item.completion_time_seconds ? `${Math.round(item.completion_time_seconds)}s` : '—'}</span>
              </div>
              <button
                className="mt-3 text-sm text-primary-600"
                onClick={() => setExpanded(expanded === item.question_id ? null : item.question_id)}
              >
                {expanded === item.question_id ? 'Hide' : 'Show'} attempt details
              </button>
              {expanded === item.question_id && item.attempts?.length > 0 && (
                <div className="mt-3">
                  <DataTable
                    columns={[
                      { key: 'clicked_at', label: 'Clicked', render: (r) => new Date(r.clicked_at).toLocaleString() },
                      { key: 'click_rank', label: 'Click Rank' },
                      { key: 'approved_rank', label: 'Approved Rank', render: (r) => r.approved_rank ?? '—' },
                      { key: 'points', label: 'Points' },
                      { key: 'status', label: 'Status', render: (r) => <Badge>{r.status}</Badge> },
                      { key: 'trainer_notes', label: 'Notes', render: (r) => r.trainer_notes || '—' },
                    ]}
                    data={item.attempts}
                  />
                </div>
              )}
            </Card>
          ))}
        </div>
      </QueryState>
    </div>
  )
}
