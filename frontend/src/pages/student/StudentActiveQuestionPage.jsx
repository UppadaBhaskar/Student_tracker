import { useState } from 'react'
import { useActiveQuestion, useCompleteQuestion } from '../../hooks'
import { getErrorMessage } from '../../api/errors'
import { Card, PageHeader, Button, Badge, Alert, QueryState } from '../../components/ui'
import QuestionTimer from '../../components/questions/QuestionTimer'

export default function StudentActiveQuestionPage() {
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  const { data, isLoading, error, refetch } = useActiveQuestion({ refetchInterval: 5000 })
  const completeMut = useCompleteQuestion()

  const q = data?.question
  const latest = data?.latest_attempt
  const canComplete = q && (!latest || latest.status === 'rejected')
  const isPending = latest?.status === 'pending'
  const isApproved = latest?.status === 'approved'

  const handleComplete = () => {
    setMsg('')
    setErr('')
    completeMut.mutate(undefined, {
      onSuccess: (attempt) => {
        setMsg(`Submitted! Click Rank: ${attempt.click_rank}, Points: ${attempt.points}. Awaiting verification.`)
        refetch()
      },
      onError: (e) => setErr(getErrorMessage(e)),
    })
  }

  return (
    <div>
      <PageHeader title="Active Question" />
      {msg && <Alert type="success" className="mb-4">{msg}</Alert>}
      {err && <Alert className="mb-4">{err}</Alert>}
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        {!q ? (
          <Card><p className="text-slate-500">No active question right now. Check back later.</p></Card>
        ) : (
          <Card>
            <div className="flex flex-wrap items-start justify-between gap-6">
              <div className="flex-1">
                <Badge color="green">ACTIVE</Badge>
                <h2 className="mt-2 text-2xl font-bold">{q.title}</h2>
                <p className="text-sm text-slate-500">{q.subject_name} · Day {q.day} · up to {q.max_points} points</p>
                <p className="mt-4 whitespace-pre-wrap text-slate-700">{q.description}</p>
                {isPending && (
                  <Alert type="info" className="mt-4">Your submission is pending trainer verification.</Alert>
                )}
                {isApproved && (
                  <Alert type="success" className="mt-4">
                    Approved! Rank: {latest.approved_rank}, Points: {latest.points}
                  </Alert>
                )}
                {latest?.status === 'rejected' && (
                  <Alert className="mt-4">Previous attempt rejected. You may try again.</Alert>
                )}
                {canComplete && !isPending && (
                  <Button className="mt-6" onClick={handleComplete} disabled={completeMut.isPending}>
                    {completeMut.isPending ? 'Submitting...' : 'Mark Complete'}
                  </Button>
                )}
              </div>
              <QuestionTimer revealedAt={q.revealed_at} timerMinutes={q.timer_minutes} />
            </div>
          </Card>
        )}
      </QueryState>
    </div>
  )
}
