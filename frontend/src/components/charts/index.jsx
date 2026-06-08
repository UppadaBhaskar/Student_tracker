import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function TrendLineChart({ data, dataKey = 'value', xKey = 'day', color = '#3b82f6', height = 280 }) {
  if (!data?.length) return <p className="text-sm text-slate-500">No chart data</p>
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function MultiLineChart({ data, lines, xKey = 'day', height = 280 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        {lines.map((l, i) => (
          <Line key={l.key} type="monotone" dataKey={l.key} name={l.name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}

export function SimpleBarChart({ data, dataKey = 'value', xKey = 'day', height = 280 }) {
  if (!data?.length) return <p className="text-sm text-slate-500">No chart data</p>
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Bar dataKey={dataKey} fill="#3b82f6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function SubjectBarChart({ data, height = 300 }) {
  if (!data?.length) return <p className="text-sm text-slate-500">No chart data</p>
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ left: 80 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="subject_name" tick={{ fontSize: 11 }} width={75} />
        <Tooltip />
        <Bar dataKey="avg_points" name="Avg Points" fill="#3b82f6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function RiskPieChart({ data }) {
  const chartData = [
    { name: 'Green', value: data?.green || 0, color: '#10b981' },
    { name: 'Yellow', value: data?.yellow || 0, color: '#f59e0b' },
    { name: 'Red', value: data?.red || 0, color: '#ef4444' },
  ].filter((d) => d.value > 0)

  if (!chartData.length) return <p className="text-sm text-slate-500">No risk data</p>
  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function ParticipationChart({ data, height = 280 }) {
  if (!data?.length) return <p className="text-sm text-slate-500">No data</p>
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="day" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Bar dataKey="attempted" stackId="a" fill="#3b82f6" name="Attempted" />
        <Bar dataKey="not_attempted" stackId="a" fill="#cbd5e1" name="Not Attempted" />
      </BarChart>
    </ResponsiveContainer>
  )
}
