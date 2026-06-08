import { useState, useEffect } from 'react'
import { useActiveQuestion, useQuestionAttempts, useApproveAttempt, useRejectAttempt } from '../../hooks'
import { Card, PageHeader, Button, Badge, QueryState } from '../../components/ui'
import { DataTable } from '../../components/ui/Table'

export default function VerificationQueuePage() {
  const [questionId, setQuestionId] = useState('')

  const { data: activeData } = useActiveQuestion()
  const { data: attempts = [], isLoading, error, refetch } = useQuestionAttempts(questionId, 'pending', {
    refetchInterval: 5000,
  })
  const approveMut = useApproveAttempt()
  const rejectMut = useRejectAttempt()

  useEffect(() => {
    if (activeData?.question?.id && !questionId) setQuestionId(String(activeData.question.id))
  }, [activeData, questionId])

  return (
    <div>
      <PageHeader title="Verification Queue" subtitle="Approve or reject student attempts" />
      <Card>
        <QueryState
          isLoading={isLoading}
          error={error}
          isEmpty={!attempts.length}
          emptyMessage="No pending verifications"
          onRetry={refetch}
        >
          <DataTable
            columns={[
              { key: 'student_name', label: 'Student' },
              { key: 'click_rank', label: 'Click Rank' },
              { key: 'points', label: 'Points' },
              { key: 'clicked_at', label: 'Clicked', render: (r) => new Date(r.clicked_at).toLocaleTimeString() },
              { key: 'status', label: 'Status', render: (r) => <Badge color="yellow">{r.status}</Badge> },
              { key: 'actions', label: 'Actions', render: (r) => (
                <div className="flex gap-2">
                  <Button
                    variant="success"
                    className="px-2 py-1 text-xs"
                    disabled={approveMut.isPending}
                    onClick={() => approveMut.mutate({ id: r.id }, { onSuccess: () => refetch() })}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="danger"
                    className="px-2 py-1 text-xs"
                    disabled={rejectMut.isPending}
                    onClick={() => rejectMut.mutate({ id: r.id }, { onSuccess: () => refetch() })}
                  >
                    Reject
                  </Button>
                </div>
              )},
            ]}
            data={attempts}
          />
        </QueryState>
      </Card>
    </div>
  )
}
