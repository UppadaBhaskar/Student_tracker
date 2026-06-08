import { Alert, Button, Empty, Loading } from './index'
import { getErrorMessage } from '../../api/errors'

export function QueryState({
  isLoading,
  isFetching,
  error,
  isEmpty,
  emptyMessage = 'No data found',
  onRetry,
  children,
  skeleton,
}) {
  if (isLoading) return skeleton || <Loading />

  if (error) {
    return (
      <div className="py-8 text-center">
        <Alert className="mx-auto mb-4 max-w-md">{getErrorMessage(error)}</Alert>
        {onRetry && <Button variant="secondary" onClick={onRetry}>Try again</Button>}
      </div>
    )
  }

  if (isEmpty) return <Empty message={emptyMessage} />

  return (
    <>
      {isFetching && <div className="mb-2 text-xs text-slate-400">Refreshing...</div>}
      {children}
    </>
  )
}

export function MutationAlert({ error, success, onDismiss }) {
  if (!error && !success) return null
  return (
    <div className="mb-4">
      {error && <Alert>{getErrorMessage(error)}</Alert>}
      {success && (
        <Alert type="success">
          {success}
          {onDismiss && <button type="button" className="ml-2 underline" onClick={onDismiss}>Dismiss</button>}
        </Alert>
      )}
    </div>
  )
}
