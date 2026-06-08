import { useActiveQuestion } from '../../hooks'
import { Card, PageHeader, Badge, QueryState } from '../../components/ui'
import QuestionTimer from '../../components/questions/QuestionTimer'

export default function ActiveQuestionPage() {
  const { data, isLoading, error, refetch } = useActiveQuestion({ refetchInterval: 10000 })

  const q = data?.question

  return (
    <div>
      <PageHeader title="Active Question" subtitle="Global active question (trainer view)" />
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        {!q ? (
          <Card><p className="text-slate-500">No active question. Reveal one from the Questions list.</p></Card>
        ) : (
          <Card>
            <div className="flex items-start justify-between">
              <div>
                <Badge color="green">ACTIVE</Badge>
                <h2 className="mt-2 text-xl font-bold">{q.title}</h2>
                <p className="text-sm text-slate-500">{q.subject_name} · Day {q.day} · {q.difficulty} · {q.max_points} pts</p>
                <p className="mt-4 text-slate-700">{q.description}</p>
              </div>
              <QuestionTimer revealedAt={q.revealed_at} timerMinutes={q.timer_minutes} />
            </div>
          </Card>
        )}
      </QueryState>
    </div>
  )
}
