import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useEntity, useCreateEntity, useUpdateEntity } from '../../hooks'
import { getErrorMessage } from '../../api/errors'
import { Card, PageHeader, Button, Input, Select, Alert } from '../../components/ui'

export default function EntityFormPage() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    name: '', entity_type: 'workshop', total_days: 15,
    start_date: '', end_date: '',
  })

  const { data: entity } = useEntity(id, { enabled: isEdit })
  const createMut = useCreateEntity()
  const updateMut = useUpdateEntity()
  const saveMut = isEdit ? updateMut : createMut

  useEffect(() => {
    if (entity) setForm({
      name: entity.name,
      entity_type: entity.entity_type,
      total_days: entity.total_days,
      start_date: entity.start_date,
      end_date: entity.end_date,
    })
  }, [entity])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    const payload = { ...form, total_days: Number(form.total_days) }
    const onSuccess = () => navigate('/trainer/entities')
    const onError = (err) => setError(getErrorMessage(err))

    if (isEdit) {
      updateMut.mutate({ id, data: payload }, { onSuccess, onError })
    } else {
      createMut.mutate(payload, { onSuccess, onError })
    }
  }

  return (
    <div>
      <PageHeader title={isEdit ? 'Edit Entity' : 'Create Entity'} />
      {error && <Alert className="mb-4">{error}</Alert>}
      <Card>
        <form onSubmit={handleSubmit} className="mx-auto max-w-lg space-y-4">
          <Input label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <Select
            label="Type"
            value={form.entity_type}
            onChange={(e) => setForm({ ...form, entity_type: e.target.value })}
            options={[
              { value: 'workshop', label: 'Workshop' },
              { value: 'bootcamp', label: 'Bootcamp' },
              { value: 'training_program', label: 'Training Program' },
            ]}
          />
          <Input label="Total Days" type="number" value={form.total_days} onChange={(e) => setForm({ ...form, total_days: e.target.value })} required />
          <Input label="Start Date" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
          <Input label="End Date" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} required />
          <div className="flex gap-3">
            <Button type="submit" disabled={saveMut.isPending}>{isEdit ? 'Update' : 'Create'}</Button>
            <Button type="button" variant="secondary" onClick={() => navigate(-1)}>Cancel</Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
