import { Link } from 'react-router-dom'
import { useEntities, useDeleteEntity } from '../../hooks'
import { Card, PageHeader, Button, DataTable, Badge, QueryState } from '../../components/ui'

export default function EntityListPage() {
  const { data: entities = [], isLoading, error, refetch } = useEntities()
  const deleteMut = useDeleteEntity()

  return (
    <div>
      <PageHeader
        title="Entities"
        subtitle="Workshops, bootcamps, and training programs"
        action={<Link to="/trainer/entities/new"><Button>Create Entity</Button></Link>}
      />
      <Card>
        <QueryState isLoading={isLoading} error={error} isEmpty={!entities.length} emptyMessage="No entities yet" onRetry={refetch}>
          <DataTable
            columns={[
              { key: 'name', label: 'Name' },
              { key: 'entity_type', label: 'Type', render: (r) => <Badge>{r.entity_type}</Badge> },
              { key: 'total_days', label: 'Days' },
              { key: 'start_date', label: 'Start' },
              { key: 'end_date', label: 'End' },
              {
                key: 'actions',
                label: 'Actions',
                render: (r) => (
                  <div className="flex gap-2">
                    <Link to={`/trainer/entities/${r.id}/edit`} className="text-primary-600 text-sm">Edit</Link>
                    <button
                      className="text-red-600 text-sm"
                      disabled={deleteMut.isPending}
                      onClick={() => confirm('Delete?') && deleteMut.mutate(r.id)}
                    >
                      Delete
                    </button>
                  </div>
                ),
              },
            ]}
            data={entities}
          />
        </QueryState>
      </Card>
    </div>
  )
}
