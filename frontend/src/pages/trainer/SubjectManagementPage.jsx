import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useSubjects, useCreateSubject, useUpdateSubject, useDeleteSubject } from '../../hooks'
import { Card, PageHeader, Button, Input, DataTable, QueryState } from '../../components/ui'

export default function SubjectManagementPage() {
  const { id: entityId } = useParams()
  const [name, setName] = useState('')
  const [editId, setEditId] = useState(null)
  const [editName, setEditName] = useState('')

  const { data: subjects = [], isLoading, error, refetch } = useSubjects(entityId)
  const createMut = useCreateSubject(entityId)
  const updateMut = useUpdateSubject(entityId)
  const deleteMut = useDeleteSubject(entityId)

  return (
    <div>
      <PageHeader title="Subjects" />
      <Card title="Add Subject" className="mb-6">
        <div className="flex gap-3">
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Subject name" className="flex-1" />
          <Button
            onClick={() => name && createMut.mutate(name, { onSuccess: () => setName('') })}
            disabled={createMut.isPending}
          >
            Add
          </Button>
        </div>
      </Card>
      <Card>
        <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
          <DataTable
            columns={[
              { key: 'name', label: 'Name', render: (r) => editId === r.id ? (
                <Input value={editName} onChange={(e) => setEditName(e.target.value)} />
              ) : r.name },
              { key: 'actions', label: 'Actions', render: (r) => (
                <div className="flex gap-2">
                  {editId === r.id ? (
                    <>
                      <Button onClick={() => updateMut.mutate({ id: r.id, name: editName }, { onSuccess: () => setEditId(null) })}>Save</Button>
                      <Button variant="secondary" onClick={() => setEditId(null)}>Cancel</Button>
                    </>
                  ) : (
                    <>
                      <button className="text-primary-600 text-sm" onClick={() => { setEditId(r.id); setEditName(r.name) }}>Edit</button>
                      <button className="text-red-600 text-sm" onClick={() => confirm('Delete?') && deleteMut.mutate(r.id)}>Delete</button>
                    </>
                  )}
                </div>
              )},
            ]}
            data={subjects}
          />
        </QueryState>
      </Card>
    </div>
  )
}
