export function DataTable({ columns, data, keyField = 'id' }) {
  if (!data?.length) return null
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {data.map((row, i) => (
            <tr key={row[keyField] ?? i} className="hover:bg-slate-50">
              {columns.map((col) => (
                <td key={col.key} className="whitespace-nowrap px-4 py-3 text-slate-700">
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function StatusToggle({ value, onChange, options }) {
  return (
    <div className="flex gap-1">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`rounded-md px-2 py-1 text-xs font-medium transition ${
            value === opt.value
              ? opt.activeClass || 'bg-primary-600 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
