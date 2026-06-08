export function Card({ title, children, className = '', action }) {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}>
      {title && (
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <h3 className="font-semibold text-slate-800">{title}</h3>
          {action}
        </div>
      )}
      <div className={title ? 'p-5' : 'p-5'}>{children}</div>
    </div>
  )
}

export function StatCard({ label, value, sub, color = 'blue' }) {
  const colors = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-emerald-50 text-emerald-700',
    yellow: 'bg-amber-50 text-amber-700',
    red: 'bg-red-50 text-red-700',
    slate: 'bg-slate-100 text-slate-700',
  }
  return (
    <div className={`rounded-xl p-4 ${colors[color] || colors.blue}`}>
      <p className="text-xs font-medium uppercase tracking-wide opacity-80">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value ?? '—'}</p>
      {sub && <p className="mt-1 text-xs opacity-70">{sub}</p>}
    </div>
  )
}

export function Button({ children, variant = 'primary', className = '', ...props }) {
  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700',
    secondary: 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    success: 'bg-emerald-600 text-white hover:bg-emerald-700',
    ghost: 'text-slate-600 hover:bg-slate-100',
  }
  return (
    <button
      className={`inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

export function Input({ label, error, className = '', ...props }) {
  return (
    <label className={`block ${className}`}>
      {label && <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>}
      <input
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        {...props}
      />
      {error && <span className="mt-1 text-xs text-red-600">{error}</span>}
    </label>
  )
}

export function Select({ label, options, className = '', ...props }) {
  return (
    <label className={`block ${className}`}>
      {label && <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>}
      <select
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
        {...props}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  )
}

export function Textarea({ label, ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>}
      <textarea
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
        rows={4}
        {...props}
      />
    </label>
  )
}

export function PageHeader({ title, subtitle, action }) {
  return (
    <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

export function Loading() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
    </div>
  )
}

export function Empty({ message = 'No data found' }) {
  return <p className="py-8 text-center text-sm text-slate-500">{message}</p>
}

export function Alert({ type = 'error', children }) {
  const styles = {
    error: 'bg-red-50 text-red-700 border-red-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
  }
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm ${styles[type]}`}>{children}</div>
  )
}

export function Badge({ children, color = 'slate' }) {
  const colors = {
    green: 'bg-emerald-100 text-emerald-800',
    yellow: 'bg-amber-100 text-amber-800',
    red: 'bg-red-100 text-red-800',
    blue: 'bg-blue-100 text-blue-800',
    slate: 'bg-slate-100 text-slate-700',
  }
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[color]}`}>
      {children}
    </span>
  )
}

export function RiskBadge({ risk }) {
  if (!risk) return <Badge color="slate">N/A</Badge>
  const map = { green: 'green', yellow: 'yellow', red: 'red' }
  return <Badge color={map[risk] || 'slate'}>{risk.toUpperCase()}</Badge>
}

export function DaySelector({ value, onChange, totalDays = 15 }) {
  const options = [{ value: '', label: 'Select day' }]
  for (let d = 1; d <= totalDays; d++) options.push({ value: d, label: `Day ${d}` })
  return (
    <Select
      label="Day"
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      options={options}
      className="w-40"
    />
  )
}

export function FileUpload({ onChange, accept = '.xlsx,.xls', disabled = false, loading = false }) {
  return (
    <div className="flex items-center gap-3">
      <input
        type="file"
        accept={accept}
        disabled={disabled || loading}
        onChange={(e) => onChange(e.target.files?.[0])}
        className="text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-primary-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-700 disabled:opacity-50"
      />
      {loading && <span className="text-xs text-slate-500">Uploading...</span>}
    </div>
  )
}

export { DataTable, StatusToggle } from './Table'
export { QueryState, MutationAlert } from './QueryState'
