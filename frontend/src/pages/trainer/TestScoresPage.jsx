import { useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  useStudents, useSubjects, useTestScores, useSaveTestScores, useImportTestScores,
} from '../../hooks'
import { useMutationFeedback } from '../../hooks/useMutationFeedback'
import { Card, PageHeader, Button, Input, FileUpload, QueryState, MutationAlert } from '../../components/ui'

export default function TestScoresPage() {
  const { id: entityId } = useParams()
  const [form, setForm] = useState({ student_id: '', subject_id: '', day: 1, score: '' })
  const { error, success, clear, wrap } = useMutationFeedback()

  const { data: students = [] } = useStudents(entityId)
  const { data: subjects = [] } = useSubjects(entityId)
  const { data: scores = [], refetch, isLoading, error: loadError } = useTestScores(entityId)
  const saveMut = wrap(useSaveTestScores(entityId), 'Score saved')
  const importMut = wrap(useImportTestScores(entityId), (r) => `Imported ${r.imported} records`)

  const handleSave = () => {
    clear()
    saveMut.mutate([{
      student_id: Number(form.student_id),
      subject_id: Number(form.subject_id),
      day: Number(form.day),
      score: Number(form.score),
    }], {
      onSuccess: () => { refetch(); setForm({ ...form, score: '' }) },
    })
  }

  const handleImport = (file) => {
    if (!file) return
    clear()
    importMut.mutate(file, { onSuccess: () => refetch() })
  }

  return (
    <div>
      <PageHeader title="Test Scores" />
      <MutationAlert error={error} success={success} onDismiss={clear} />
      <Card title="Add / Update Score" className="mb-6">
        <div className="grid gap-4 md:grid-cols-5">
          <select className="rounded border px-3 py-2 text-sm" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })}>
            <option value="">Student</option>
            {students.map((s) => <option key={s.id} value={s.id}>{s.full_name}</option>)}
          </select>
          <select className="rounded border px-3 py-2 text-sm" value={form.subject_id} onChange={(e) => setForm({ ...form, subject_id: e.target.value })}>
            <option value="">Subject</option>
            {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <Input type="number" placeholder="Day" value={form.day} onChange={(e) => setForm({ ...form, day: e.target.value })} />
          <Input type="number" placeholder="Score" value={form.score} onChange={(e) => setForm({ ...form, score: e.target.value })} />
          <Button onClick={handleSave} disabled={saveMut.isPending}>Save</Button>
        </div>
        <div className="mt-4">
          <FileUpload onChange={handleImport} />
        </div>
      </Card>
      <Card title="All Test Scores">
        <QueryState isLoading={isLoading} error={loadError} onRetry={refetch}>
          <div className="overflow-x-auto text-sm">
            <table className="min-w-full">
              <thead><tr className="border-b"><th className="px-3 py-2 text-left">Student</th><th>Subject</th><th>Day</th><th>Score</th></tr></thead>
              <tbody>
                {scores.map((s, i) => (
                  <tr key={i} className="border-b">
                    <td className="px-3 py-2">{students.find((st) => st.id === s.student_id)?.full_name || s.student_id}</td>
                    <td className="px-3 py-2">{subjects.find((sub) => sub.id === s.subject_id)?.name || s.subject_id}</td>
                    <td className="px-3 py-2">{s.day}</td>
                    <td className="px-3 py-2">{s.score}</td>
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
