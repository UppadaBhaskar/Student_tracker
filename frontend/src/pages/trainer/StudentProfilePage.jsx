import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useStudent, useStudentTrends, useAddRemark } from '../../hooks'
import { Card, PageHeader, Button, Input, QueryState, RiskBadge } from '../../components/ui'
import { TrendLineChart } from '../../components/charts'
import RiskBreakdown from '../../components/RiskBreakdown'

export default function StudentProfilePage() {
  const { sid } = useParams()
  const [remark, setRemark] = useState('')

  const { data, isLoading, error, refetch } = useStudent(sid)
  const { data: trends } = useStudentTrends(sid)
  const remarkMut = useAddRemark(sid)

  const student = data?.student
  const risk = data?.risk

  return (
    <div>
      <PageHeader
        title={student?.full_name || 'Student Profile'}
        subtitle={student ? `USN: ${student.usn}` : undefined}
        action={risk && <RiskBadge risk={risk.overall} />}
      />
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Profile">
            <dl className="space-y-2 text-sm">
              <div><dt className="text-slate-500">Email</dt><dd>{student?.email}</dd></div>
              <div><dt className="text-slate-500">College</dt><dd>{student?.college || '—'}</dd></div>
              <div><dt className="text-slate-500">Branch</dt><dd>{student?.branch || '—'}</dd></div>
            </dl>
          </Card>
          <Card title="Risk Assessment">
            <RiskBreakdown risk={risk} />
          </Card>
          <Card title="Remarks">
            <div className="mb-4 flex gap-2">
              <Input value={remark} onChange={(e) => setRemark(e.target.value)} placeholder="Add remark..." className="flex-1" />
              <Button
                disabled={!remark || remarkMut.isPending}
                onClick={() => remarkMut.mutate(remark, { onSuccess: () => setRemark('') })}
              >
                Add
              </Button>
            </div>
            <ul className="space-y-2">
              {(data?.remarks || []).map((r) => (
                <li key={r.id} className="rounded-lg bg-slate-50 px-3 py-2 text-sm">
                  <p>{r.remark}</p>
                  <p className="text-xs text-slate-400">{new Date(r.created_at).toLocaleString()}</p>
                </li>
              ))}
            </ul>
          </Card>
          {trends && (
            <Card title="Attendance Trend" className="lg:col-span-2">
              <TrendLineChart data={trends.attendance_trend?.filter((d) => d.value != null)} dataKey="value" />
            </Card>
          )}
        </div>
      </QueryState>
    </div>
  )
}
