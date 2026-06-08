import { Link } from 'react-router-dom'
import { useParams } from 'react-router-dom'
import { useStudents, useDeleteStudent } from '../../hooks'
import { Card, PageHeader, Button, DataTable, QueryState } from '../../components/ui'

export default function StudentListPage() {
  const { id: entityId } = useParams()
  const { data: students = [], isLoading, error, refetch } = useStudents(entityId)
  const deleteMut = useDeleteStudent(entityId)

  return (
    <div>
      <PageHeader
        title="Students"
        action={<Link to={`/trainer/entities/${entityId}/students/new`}><Button>Add Student</Button></Link>}
      />
      <Card>
        <QueryState isLoading={isLoading} error={error} isEmpty={!students.length} emptyMessage="No students yet" onRetry={refetch}>
          <DataTable
            columns={[
              { key: 'usn', label: 'USN' },
              { key: 'full_name', label: 'Name' },
              { key: 'email', label: 'Email' },
              { key: 'college', label: 'College' },
              { key: 'branch', label: 'Branch' },
              {
                key: 'actions', label: 'Actions',
                render: (r) => (
                  <div className="flex gap-2">
                    <Link to={`/trainer/entities/${entityId}/students/${r.id}`} className="text-primary-600 text-sm">Profile</Link>
                    <Link to={`/trainer/entities/${entityId}/students/${r.id}/edit`} className="text-primary-600 text-sm">Edit</Link>
                    <button className="text-red-600 text-sm" onClick={() => confirm('Delete?') && deleteMut.mutate(r.id)}>Delete</button>
                  </div>
                ),
              },
            ]}
            data={students}
          />
        </QueryState>
      </Card>
    </div>
  )
}
