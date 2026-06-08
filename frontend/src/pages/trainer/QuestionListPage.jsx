import { Link } from 'react-router-dom'
import { useParams } from 'react-router-dom'
import { useQuestions, useRevealQuestion, useArchiveQuestion, useDeleteQuestion } from '../../hooks'
import { Card, PageHeader, Button, DataTable, Badge, QueryState } from '../../components/ui'

export default function QuestionListPage() {
  const { id: entityId } = useParams()
  const { data: questions = [], isLoading, error, refetch } = useQuestions(entityId)
  const revealMut = useRevealQuestion(entityId)
  const archiveMut = useArchiveQuestion(entityId)
  const deleteMut = useDeleteQuestion(entityId)

  return (
    <div>
      <PageHeader
        title="Questions"
        action={<Link to={`/trainer/entities/${entityId}/questions/new`}><Button>Add Question</Button></Link>}
      />
      <Card>
        <QueryState isLoading={isLoading} error={error} isEmpty={!questions.length} emptyMessage="No questions yet" onRetry={refetch}>
          <DataTable
            columns={[
              { key: 'question_number', label: '#' },
              { key: 'title', label: 'Title' },
              { key: 'subject_name', label: 'Subject' },
              { key: 'day', label: 'Day' },
              { key: 'difficulty', label: 'Difficulty', render: (r) => <Badge>{r.difficulty}</Badge> },
              { key: 'max_points', label: 'Points' },
              { key: 'status', label: 'Status', render: (r) => (
                <Badge color={r.status === 'active' ? 'green' : r.status === 'archived' ? 'slate' : 'blue'}>{r.status}</Badge>
              )},
              { key: 'actions', label: 'Actions', render: (r) => (
                <div className="flex flex-wrap gap-2">
                  <Link to={`/trainer/entities/${entityId}/questions/${r.id}/edit`} className="text-primary-600 text-sm">Edit</Link>
                  {r.status !== 'active' && (
                    <button className="text-emerald-600 text-sm" onClick={() => confirm('Reveal this question globally?') && revealMut.mutate(r.id)}>Reveal</button>
                  )}
                  {r.status === 'active' && (
                    <button className="text-amber-600 text-sm" onClick={() => archiveMut.mutate(r.id)}>Archive</button>
                  )}
                  {r.status !== 'active' && (
                    <button className="text-red-600 text-sm" onClick={() => confirm('Delete?') && deleteMut.mutate(r.id)}>Delete</button>
                  )}
                </div>
              )},
            ]}
            data={questions}
          />
        </QueryState>
      </Card>
    </div>
  )
}
