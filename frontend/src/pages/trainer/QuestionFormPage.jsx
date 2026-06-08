import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useSubjects, useQuestions, useCreateQuestion, useUpdateQuestion } from '../../hooks'
import { getErrorMessage } from '../../api/errors'
import { Card, PageHeader, Button, Input, Select, Textarea, Alert } from '../../components/ui'

export default function QuestionFormPage() {
  const { id: entityId, qid } = useParams()
  const isEdit = Boolean(qid)
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    question_number: 1, subject_id: '', title: '', description: '',
    day: 1, timer_minutes: 30, difficulty: 'medium', max_points: 10,
  })

  const { data: subjects = [] } = useSubjects(entityId)
  const { data: questions = [] } = useQuestions(entityId, { enabled: isEdit })
  const createMut = useCreateQuestion(entityId)
  const updateMut = useUpdateQuestion(entityId)

  useEffect(() => {
    if (isEdit && questions.length) {
      const q = questions.find((x) => x.id === Number(qid))
      if (q) setForm({
        question_number: q.question_number, subject_id: q.subject_id, title: q.title,
        description: q.description || '', day: q.day, timer_minutes: q.timer_minutes,
        difficulty: q.difficulty, max_points: q.max_points,
      })
    }
  }, [questions, qid, isEdit])

  useEffect(() => {
    if (subjects.length && !form.subject_id) setForm((f) => ({ ...f, subject_id: subjects[0].id }))
  }, [subjects, form.subject_id])

  const difficultyPoints = { easy: 5, medium: 10, hard: 20 }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    const payload = {
      ...form,
      question_number: Number(form.question_number),
      subject_id: Number(form.subject_id),
      day: Number(form.day),
      timer_minutes: Number(form.timer_minutes),
      max_points: Number(form.max_points),
    }
    const onSuccess = () => navigate(`/trainer/entities/${entityId}/questions`)
    const onError = (err) => setError(getErrorMessage(err))

    if (isEdit) {
      updateMut.mutate({ id: qid, data: payload }, { onSuccess, onError })
    } else {
      createMut.mutate(payload, { onSuccess, onError })
    }
  }

  const handleDifficulty = (d) => {
    setForm({ ...form, difficulty: d, max_points: difficultyPoints[d] })
  }

  const isPending = createMut.isPending || updateMut.isPending

  return (
    <div>
      <PageHeader title={isEdit ? 'Edit Question' : 'Create Question'} />
      {error && <Alert className="mb-4">{error}</Alert>}
      <Card>
        <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-4">
          <Input label="Question Number" type="number" value={form.question_number} onChange={(e) => setForm({ ...form, question_number: e.target.value })} required />
          <Select label="Subject" value={form.subject_id} onChange={(e) => setForm({ ...form, subject_id: e.target.value })} options={subjects.map((s) => ({ value: s.id, label: s.name }))} />
          <Input label="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          <Textarea label="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <Input label="Day" type="number" value={form.day} onChange={(e) => setForm({ ...form, day: e.target.value })} required />
          <Input label="Timer (minutes)" type="number" value={form.timer_minutes} onChange={(e) => setForm({ ...form, timer_minutes: e.target.value })} required />
          <Select label="Difficulty" value={form.difficulty} onChange={(e) => handleDifficulty(e.target.value)} options={[
            { value: 'easy', label: 'Easy (5 pts)' },
            { value: 'medium', label: 'Medium (10 pts)' },
            { value: 'hard', label: 'Hard (20 pts)' },
          ]} />
          <Input label="Max Points" type="number" value={form.max_points} onChange={(e) => setForm({ ...form, max_points: e.target.value })} />
          <div className="flex gap-3">
            <Button type="submit" disabled={isPending}>{isEdit ? 'Update' : 'Create'}</Button>
            <Button type="button" variant="secondary" onClick={() => navigate(-1)}>Cancel</Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
