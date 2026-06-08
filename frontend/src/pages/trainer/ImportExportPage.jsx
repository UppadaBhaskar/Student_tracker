import { useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  useImportStudents, useImportQuestions, useImportTestScores,
  useExportEntity, useImportTemplate,
} from '../../hooks'
import { useMutationFeedback } from '../../hooks/useMutationFeedback'
import { downloadBlob } from '../../api/endpoints'
import { getErrorMessage } from '../../api/errors'
import { Card, PageHeader, Button, FileUpload, MutationAlert, Alert } from '../../components/ui'

const EXPORT_TYPES = [
  'students', 'attendance', 'assignments', 'presentations', 'test-scores',
  'question-results', 'question-attempts', 'leaderboard', 'analytics-summary',
]

const IMPORT_CONFIG = [
  {
    key: 'students',
    title: 'Import Students',
    columns: 'USN, Name, College, Branch, Email, Password',
    hook: 'students',
  },
  {
    key: 'questions',
    title: 'Import Questions',
    columns: 'Question Number, Subject, Question, Day, Timer, Difficulty (optional)',
    hook: 'questions',
  },
  {
    key: 'test-scores',
    title: 'Import Test Scores',
    columns: 'Student, Subject, Day, Score',
    hook: 'tests',
  },
]

export default function ImportExportPage() {
  const { id: entityId } = useParams()
  const [importErrors, setImportErrors] = useState([])
  const [exportingType, setExportingType] = useState(null)
  const { error, success, clear, wrap, setError } = useMutationFeedback()

  const importStudentsMut = useImportStudents(entityId)
  const importQuestionsMut = useImportQuestions(entityId)
  const importTestsMut = useImportTestScores(entityId)
  const exportMut = useExportEntity()
  const templateMut = useImportTemplate()

  const importStudents = wrap(importStudentsMut, (r) => {
    setImportErrors(r.errors || [])
    return `Imported ${r.created} students${r.errors?.length ? `. ${r.errors.length} row errors.` : ''}`
  })
  const importQuestions = wrap(importQuestionsMut, (r) => {
    setImportErrors(r.errors || [])
    return `Imported ${r.created} questions${r.errors?.length ? `. ${r.errors.length} row errors.` : ''}`
  })
  const importTests = wrap(importTestsMut, (r) => {
    setImportErrors(r.errors || [])
    return `Imported ${r.imported} test scores${r.errors?.length ? `. ${r.errors.length} row errors.` : ''}`
  })

  const handleImport = (mutator, file) => {
    if (!file) return
    clear()
    setImportErrors([])
    mutator.mutate(file)
  }

  const handleExport = async (type) => {
    clear()
    setExportingType(type)
    try {
      const res = await exportMut.mutateAsync({ entityId, type })
      downloadBlob(res, `${type}.xlsx`)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setExportingType(null)
    }
  }

  const handleTemplate = async (type) => {
    clear()
    try {
      const res = await templateMut.mutateAsync(type)
      downloadBlob(res, `${type}_template.xlsx`)
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  const importMutators = {
    students: importStudents,
    questions: importQuestions,
    tests: importTests,
  }

  const importPending = {
    students: importStudentsMut.isPending,
    questions: importQuestionsMut.isPending,
    tests: importTestsMut.isPending,
  }

  return (
    <div>
      <PageHeader title="Import / Export" subtitle="Excel bulk operations for workshop data" />
      <MutationAlert error={error} success={success} onDismiss={clear} />

      {importErrors.length > 0 && (
        <Alert className="mb-4">
          <p className="mb-2 font-medium">Import row errors:</p>
          <ul className="max-h-32 overflow-y-auto text-xs">
            {importErrors.map((e, i) => (
              <li key={i}>Row {e.row}: {e.error}</li>
            ))}
          </ul>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {IMPORT_CONFIG.map(({ key, title, columns, hook }) => (
          <Card key={key} title={title}>
            <p className="mb-3 text-xs text-slate-500">Columns: {columns}</p>
            <div className="mb-3">
              <Button variant="secondary" className="text-xs" onClick={() => handleTemplate(key)} disabled={templateMut.isPending}>
                Download template
              </Button>
            </div>
            <FileUpload
              onChange={(f) => handleImport(importMutators[hook], f)}
              loading={importPending[hook]}
              disabled={importPending[hook]}
            />
          </Card>
        ))}

        <Card title="Export Data" className="lg:col-span-2">
          <p className="mb-3 text-xs text-slate-500">Download current entity data as Excel files.</p>
          <div className="flex flex-wrap gap-2">
            {EXPORT_TYPES.map((t) => (
              <Button
                key={t}
                variant="secondary"
                className="text-xs"
                onClick={() => handleExport(t)}
                disabled={exportMut.isPending && exportingType === t}
              >
                {exportingType === t ? 'Exporting...' : t}
              </Button>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
