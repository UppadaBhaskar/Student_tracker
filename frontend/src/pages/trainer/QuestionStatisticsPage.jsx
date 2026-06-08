import { useParams } from 'react-router-dom'
import { useQuestionStatistics } from '../../hooks'
import { Card, PageHeader, DataTable, QueryState } from '../../components/ui'

export default function QuestionStatisticsPage() {
  const { id: entityId } = useParams()
  const { data: stats = [], isLoading, error, refetch } = useQuestionStatistics(entityId)

  return (
    <div>
      <PageHeader title="Question Statistics" />
      <Card>
        <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
          <DataTable
            columns={[
              { key: 'title', label: 'Question' },
              { key: 'subject', label: 'Subject' },
              { key: 'day', label: 'Day' },
              { key: 'attempted_students', label: 'Attempted' },
              { key: 'approved_students', label: 'Approved' },
              { key: 'pending_attempts', label: 'Pending' },
              { key: 'rejected_attempts', label: 'Rejected' },
              { key: 'avg_points', label: 'Avg Points', render: (r) => r.avg_points?.toFixed(1) ?? '—' },
              { key: 'fastest', label: 'Fastest', render: (r) => r.fastest_student?.student_name ?? '—' },
            ]}
            data={stats}
            keyField="question_id"
          />
        </QueryState>
      </Card>
    </div>
  )
}
