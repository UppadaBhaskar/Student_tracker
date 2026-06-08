import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useDailyNotes, useSaveDailyNotes } from '../../hooks'
import { useMutationFeedback } from '../../hooks/useMutationFeedback'
import { useEntity } from '../../context/EntityContext'
import { Card, PageHeader, Button, Textarea, DaySelector, MutationAlert } from '../../components/ui'

export default function DailyNotesPage() {
  const { id: entityId } = useParams()
  const { entity } = useEntity()
  const [day, setDay] = useState(1)
  const [notes, setNotes] = useState('')
  const { error, success, clear, wrap } = useMutationFeedback()

  const { data: savedNotes = '', isFetching } = useDailyNotes(entityId, day)
  const saveMut = wrap(useSaveDailyNotes(entityId, day), 'Notes saved')

  useEffect(() => {
    setNotes(savedNotes)
  }, [savedNotes, day])

  const handleSave = () => {
    clear()
    saveMut.mutate(notes)
  }

  return (
    <div>
      <PageHeader title="Daily Notes" action={
        <DaySelector value={day} onChange={setDay} totalDays={entity?.total_days || 15} />
      } />
      <MutationAlert error={error} success={success} onDismiss={clear} />
      <Card>
        {isFetching && <p className="mb-2 text-xs text-slate-400">Loading notes...</p>}
        <Textarea label={`Notes for Day ${day}`} value={notes} onChange={(e) => setNotes(e.target.value)} />
        <Button className="mt-4" onClick={handleSave} disabled={saveMut.isPending}>Save Notes</Button>
      </Card>
    </div>
  )
}
