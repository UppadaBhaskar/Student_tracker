import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAnalytics } from '../../hooks'
import { useEntity } from '../../context/EntityContext'
import { Card, PageHeader, Select, QueryState } from '../../components/ui'
import { TrendLineChart, SimpleBarChart, SubjectBarChart, RiskPieChart, ParticipationChart } from '../../components/charts'

export default function AnalyticsPage() {
  const { id: entityId } = useParams()
  const { entity } = useEntity()
  const [day, setDay] = useState('all')

  const dayOptions = [{ value: 'all', label: 'All Days' }]
  for (let d = 1; d <= (entity?.total_days || 15); d++) dayOptions.push({ value: String(d), label: `Day ${d}` })

  const { data, isLoading, error, refetch } = useAnalytics(entityId, day)

  return (
    <div>
      <PageHeader title="Analytics" action={
        <Select value={day} onChange={(e) => setDay(e.target.value)} options={dayOptions} className="w-40" />
      } />
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Attendance Trend"><TrendLineChart data={data?.attendance_trend} color="#10b981" /></Card>
          <Card title="Assignment Trend"><TrendLineChart data={data?.assignment_trend} color="#3b82f6" /></Card>
          <Card title="Presentation Trend"><TrendLineChart data={data?.presentation_trend} /></Card>
          <Card title="Test Score Trend"><TrendLineChart data={data?.test_trend} color="#8b5cf6" /></Card>
          <Card title="Question Performance"><TrendLineChart data={data?.question_performance_trend} color="#f59e0b" /></Card>
          <Card title="Question Participation"><ParticipationChart data={data?.question_participation_trend} /></Card>
          <Card title="Risk Distribution"><RiskPieChart data={data?.risk_distribution} /></Card>
          <Card title="Subject Difficulty"><SubjectBarChart data={data?.subject_difficulty_analysis} /></Card>
          <Card title="Top Students by Points">
            <SimpleBarChart data={data?.top_students_by_points?.map((s) => ({ day: s.student_name?.slice(0, 10), value: s.total_points }))} xKey="day" />
          </Card>
          <Card title="Top Students by Avg Rank">
            <SimpleBarChart data={data?.top_students_by_avg_rank?.map((s) => ({ day: s.student_name?.slice(0, 10), value: s.avg_approved_rank }))} xKey="day" />
          </Card>
        </div>
      </QueryState>
    </div>
  )
}
