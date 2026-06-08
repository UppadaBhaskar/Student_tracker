import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useDailySummary } from '../../hooks'
import { useEntity } from '../../context/EntityContext'
import { Card, PageHeader, Select, StatCard, Badge, QueryState } from '../../components/ui'
import { TrendLineChart, RiskPieChart } from '../../components/charts'

export default function DailySummaryPage() {
  const { id: entityId } = useParams()
  const { entity } = useEntity()
  const [day, setDay] = useState('all')

  const dayOptions = [{ value: 'all', label: 'All Days' }]
  for (let d = 1; d <= (entity?.total_days || 15); d++) dayOptions.push({ value: String(d), label: `Day ${d}` })

  const { data, isLoading, error, refetch } = useDailySummary(entityId, day)
  const latest = data?.days?.[data.days.length - 1]

  return (
    <div>
      <PageHeader title="Daily Summary" subtitle="Management presentation view" action={
        <Select value={day} onChange={(e) => setDay(e.target.value)} options={dayOptions} className="w-40" />
      } />
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        {latest && (
          <>
            <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
              <StatCard label="Total Students" value={latest.total_students} />
              <StatCard label="Present" value={latest.present_students} color="green" />
              <StatCard label="Attendance %" value={`${latest.attendance_pct}%`} />
              <StatCard label="Assignment %" value={`${latest.assignment_completion_pct}%`} />
              <StatCard label="Avg Presentation" value={latest.avg_presentation_score ?? '—'} />
              <StatCard label="Avg Test" value={latest.avg_test_score ?? '—'} />
              <StatCard label="Avg Question Pts" value={latest.avg_question_points ?? '—'} />
            </div>
            {latest.notes && (
              <Card title="Trainer Notes" className="mb-6">
                <p className="text-sm text-slate-700">{latest.notes}</p>
              </Card>
            )}
          </>
        )}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Daily Attendance">
            <TrendLineChart data={data?.days?.map((d) => ({ day: d.day, value: d.attendance_pct }))} />
          </Card>
          <Card title="Risk Distribution">
            <RiskPieChart data={data?.risk_counts} />
            <div className="mt-4 flex gap-4 text-sm">
              <Badge color="green">Green: {data?.risk_counts?.green}</Badge>
              <Badge color="yellow">Yellow: {data?.risk_counts?.yellow}</Badge>
              <Badge color="red">Red: {data?.risk_counts?.red}</Badge>
            </div>
          </Card>
        </div>
      </QueryState>
    </div>
  )
}
