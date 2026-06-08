import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useStudents, useSubjects, usePresentations, useSavePresentations } from '../../hooks'
import { useMutationFeedback } from '../../hooks/useMutationFeedback'
import { useEntity } from '../../context/EntityContext'
import { Card, PageHeader, Button, DaySelector, QueryState, MutationAlert } from '../../components/ui'

export default function PresentationsPage() {
  const { id: entityId } = useParams()
  const { entity } = useEntity()
  const [day, setDay] = useState(1)
  const [scores, setScores] = useState({})
  const { error, success, clear, wrap } = useMutationFeedback()

  const { data: students = [] } = useStudents(entityId)
  const { data: subjects = [] } = useSubjects(entityId)
  const { data: records = [], refetch, isLoading, error: loadError } = usePresentations(entityId, day)
  const saveMut = wrap(useSavePresentations(entityId), 'Saved')

  const handleSave = () => {
    clear()
    const recs = []
    students.forEach((s) => {
      subjects.forEach((sub) => {
        const key = `${s.id}-${sub.id}`
        if (scores[key] !== undefined && scores[key] !== '') {
          recs.push({ student_id: s.id, subject_id: sub.id, day, score: Number(scores[key]) })
        }
      })
    })
    records.forEach((r) => {
      const key = `${r.student_id}-${r.subject_id}`
      if (scores[key] === undefined) {
        recs.push({ student_id: r.student_id, subject_id: r.subject_id, day: r.day, score: r.score })
      }
    })
    saveMut.mutate(recs.length ? recs : records, { onSuccess: () => refetch() })
  }

  return (
    <div>
      <PageHeader title="Presentation Scores" action={
        <div className="flex gap-3">
          <DaySelector value={day} onChange={setDay} totalDays={entity?.total_days || 15} />
          <Button onClick={handleSave} disabled={saveMut.isPending}>Save</Button>
        </div>
      } />
      <MutationAlert error={error} success={success} onDismiss={clear} />
      <Card>
        <QueryState isLoading={isLoading} error={loadError} onRetry={refetch}>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="px-3 py-2 text-left">Student</th>
                  {subjects.map((s) => <th key={s.id} className="px-3 py-2">{s.name}</th>)}
                </tr>
              </thead>
              <tbody>
                {students.map((st) => (
                  <tr key={st.id} className="border-b">
                    <td className="px-3 py-2">{st.full_name}</td>
                    {subjects.map((sub) => {
                      const existing = records.find((r) => r.student_id === st.id && r.subject_id === sub.id)
                      const key = `${st.id}-${sub.id}`
                      return (
                        <td key={sub.id} className="px-3 py-2">
                          <input
                            type="number"
                            className="w-20 rounded border px-2 py-1"
                            defaultValue={existing?.score ?? ''}
                            onChange={(e) => setScores({ ...scores, [key]: e.target.value })}
                          />
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </QueryState>
      </Card>
    </div>
  )
}
