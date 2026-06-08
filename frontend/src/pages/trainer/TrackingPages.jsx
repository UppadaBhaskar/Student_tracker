import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useStudents, useAttendance, useSaveAttendance, useAssignments, useSaveAssignments } from '../../hooks'
import { useMutationFeedback } from '../../hooks/useMutationFeedback'
import { useEntity } from '../../context/EntityContext'
import { Card, PageHeader, Button, DaySelector, QueryState, MutationAlert } from '../../components/ui'
import { DataTable, StatusToggle } from '../../components/ui/Table'

function TrackingGridPage({ title, useRecordsHook, useSaveHook, options }) {
  const { id: entityId } = useParams()
  const { entity } = useEntity()
  const [day, setDay] = useState(1)
  const [rows, setRows] = useState({})
  const { error, success, clear, wrap } = useMutationFeedback()

  const { data: students = [], isLoading: loadingStudents, error: studentsError, refetch: refetchStudents } = useStudents(entityId)
  const { data: records = [], isLoading: loadingRecords, refetch, error: recordsError } = useRecordsHook(entityId, day)
  const saveMut = wrap(useSaveHook(entityId, day), 'Saved successfully')

  useEffect(() => {
    const map = {}
    records.forEach((r) => { map[r.student_id] = r.status })
    setRows(map)
  }, [records])

  const handleSave = () => {
    clear()
    saveMut.mutate(students.map((s) => ({ student_id: s.id, status: rows[s.id] || options[0].value })), {
      onSuccess: () => refetch(),
    })
  }

  return (
    <div>
      <PageHeader title={title} action={
        <div className="flex items-end gap-3">
          <DaySelector value={day} onChange={setDay} totalDays={entity?.total_days || 15} />
          <Button onClick={handleSave} disabled={saveMut.isPending}>Save All</Button>
        </div>
      } />
      <MutationAlert error={error} success={success} onDismiss={clear} />
      <Card>
        <QueryState
          isLoading={loadingStudents}
          error={studentsError}
          onRetry={refetchStudents}
        >
          {loadingRecords ? (
            <QueryState isLoading />
          ) : (
            <QueryState error={recordsError} onRetry={refetch}>
              <DataTable
                columns={[
                  { key: 'usn', label: 'USN' },
                  { key: 'full_name', label: 'Name' },
                  {
                    key: 'status', label: 'Status',
                    render: (s) => (
                      <StatusToggle
                        value={rows[s.id] || options[0].value}
                        onChange={(v) => setRows({ ...rows, [s.id]: v })}
                        options={options}
                      />
                    ),
                  },
                ]}
                data={students}
              />
            </QueryState>
          )}
        </QueryState>
      </Card>
    </div>
  )
}

export function AttendancePage() {
  return (
    <TrackingGridPage
      title="Attendance"
      useRecordsHook={useAttendance}
      useSaveHook={useSaveAttendance}
      options={[
        { value: 'present', label: 'Present', activeClass: 'bg-emerald-600 text-white' },
        { value: 'absent', label: 'Absent', activeClass: 'bg-red-600 text-white' },
      ]}
    />
  )
}

export function AssignmentsPage() {
  return (
    <TrackingGridPage
      title="Assignments"
      useRecordsHook={useAssignments}
      useSaveHook={useSaveAssignments}
      options={[
        { value: 'completed', label: 'Completed', activeClass: 'bg-emerald-600 text-white' },
        { value: 'not_completed', label: 'Not Done', activeClass: 'bg-slate-500 text-white' },
      ]}
    />
  )
}
