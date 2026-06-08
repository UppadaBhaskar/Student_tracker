import { useState, useEffect } from 'react'

/** Parse API ISO timestamps as UTC (backend stores UTC; naive strings lack Z). */
export function parseUtcTimestamp(iso) {
  if (!iso) return null
  const s = String(iso).trim()
  if (s.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(s)) {
    const ms = Date.parse(s)
    return Number.isNaN(ms) ? null : ms
  }
  const ms = Date.parse(`${s}Z`)
  return Number.isNaN(ms) ? null : ms
}

export default function QuestionTimer({ revealedAt, timerMinutes = 30 }) {
  const [remaining, setRemaining] = useState(null)
  const total = Math.max(1, (timerMinutes || 30) * 60)

  useEffect(() => {
    const startMs = parseUtcTimestamp(revealedAt)
    if (!startMs) {
      setRemaining(null)
      return
    }

    const tick = () => {
      const elapsed = Math.max(0, Math.floor((Date.now() - startMs) / 1000))
      setRemaining(Math.max(0, total - elapsed))
    }

    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [revealedAt, total])

  if (!revealedAt) {
    return (
      <div className="rounded-xl bg-slate-100 px-6 py-4 text-center">
        <p className="text-xs font-medium uppercase text-slate-500">Timer</p>
        <p className="text-sm text-slate-500">Not started</p>
      </div>
    )
  }

  if (remaining === null) {
    return (
      <div className="rounded-xl bg-slate-100 px-6 py-4 text-center">
        <p className="text-xs font-medium uppercase text-slate-500">Timer</p>
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    )
  }

  const mins = Math.floor(remaining / 60)
  const secs = remaining % 60
  const expired = remaining === 0
  const pct = Math.round((remaining / total) * 100)

  return (
    <div className={`rounded-xl px-6 py-4 text-center min-w-[120px] ${expired ? 'bg-red-50' : 'bg-blue-50'}`}>
      <p className="text-xs font-medium uppercase text-slate-500">Time Remaining</p>
      <p className={`text-3xl font-bold tabular-nums ${expired ? 'text-red-600' : 'text-primary-700'}`}>
        {String(mins).padStart(2, '0')}:{String(secs).padStart(2, '0')}
      </p>
      {!expired && (
        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
          <div className="h-full rounded-full bg-primary-500 transition-all duration-1000" style={{ width: `${pct}%` }} />
        </div>
      )}
      {expired && <p className="text-xs text-red-500">Time expired</p>}
    </div>
  )
}
