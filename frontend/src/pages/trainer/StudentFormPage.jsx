import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useStudent, useCreateStudent, useUpdateStudent } from '../../hooks'
import { getErrorMessage } from '../../api/errors'
import { Card, PageHeader, Button, Input, Alert } from '../../components/ui'

export default function StudentFormPage() {
  const { id: entityId, sid } = useParams()
  const isEdit = Boolean(sid)
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    usn: '', full_name: '', college: '', branch: '', email: '', password: '',
  })

  const { data: profile } = useStudent(sid, { enabled: isEdit })
  const createMut = useCreateStudent(entityId)
  const updateMut = useUpdateStudent(entityId)

  useEffect(() => {
    if (profile?.student) {
      const s = profile.student
      setForm({ usn: s.usn, full_name: s.full_name, college: s.college || '', branch: s.branch || '', email: s.email, password: '' })
    }
  }, [profile])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    const payload = { ...form }
    if (isEdit && !payload.password) delete payload.password

    const onSuccess = () => navigate(`/trainer/entities/${entityId}/students`)
    const onError = (err) => setError(getErrorMessage(err))

    if (isEdit) {
      updateMut.mutate({ id: sid, data: payload }, { onSuccess, onError })
    } else {
      createMut.mutate(payload, { onSuccess, onError })
    }
  }

  const isPending = createMut.isPending || updateMut.isPending

  return (
    <div>
      <PageHeader title={isEdit ? 'Edit Student' : 'Add Student'} />
      {error && <Alert className="mb-4">{error}</Alert>}
      <Card>
        <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-4">
          <Input label="USN" value={form.usn} onChange={(e) => setForm({ ...form, usn: e.target.value })} required />
          <Input label="Full Name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
          <Input label="College" value={form.college} onChange={(e) => setForm({ ...form, college: e.target.value })} />
          <Input label="Branch" value={form.branch} onChange={(e) => setForm({ ...form, branch: e.target.value })} />
          <Input label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input label={isEdit ? 'Password (leave blank to keep)' : 'Password'} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required={!isEdit} />
          <div className="flex gap-3">
            <Button type="submit" disabled={isPending}>{isEdit ? 'Update' : 'Create'}</Button>
            <Button type="button" variant="secondary" onClick={() => navigate(-1)}>Cancel</Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
