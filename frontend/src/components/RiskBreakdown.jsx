import { Badge } from './ui'

const DIMENSION_LABELS = {
  attendance: 'Attendance',
  assignments: 'Assignments',
  tests: 'Tests',
  questions: 'Questions',
}

export default function RiskBreakdown({ risk }) {
  if (!risk) return <p className="text-sm text-slate-500">Risk data unavailable</p>

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-slate-500">Overall:</span>
        <Badge color={risk.overall === 'green' ? 'green' : risk.overall === 'yellow' ? 'yellow' : 'red'}>
          {risk.overall?.toUpperCase()}
        </Badge>
      </div>
      {risk.dimensions && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(risk.dimensions).map(([key, level]) => (
            <Badge key={key} color={level === 'green' ? 'green' : level === 'yellow' ? 'yellow' : 'red'}>
              {DIMENSION_LABELS[key] || key}: {level}
            </Badge>
          ))}
        </div>
      )}
      {risk.metrics && (
        <dl className="grid grid-cols-2 gap-2 text-sm">
          {risk.metrics.attendance_pct != null && (
            <div><dt className="text-slate-500">Attendance</dt><dd>{risk.metrics.attendance_pct}%</dd></div>
          )}
          {risk.metrics.assignment_pct != null && (
            <div><dt className="text-slate-500">Assignments</dt><dd>{risk.metrics.assignment_pct}%</dd></div>
          )}
          {risk.metrics.test_pct != null && (
            <div><dt className="text-slate-500">Tests</dt><dd>{risk.metrics.test_pct}%</dd></div>
          )}
          {risk.metrics.question_performance_pct != null && (
            <div><dt className="text-slate-500">Questions</dt><dd>{risk.metrics.question_performance_pct}%</dd></div>
          )}
        </dl>
      )}
    </div>
  )
}
