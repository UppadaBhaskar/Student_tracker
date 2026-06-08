export class ApiError extends Error {
  constructor(message, status = 0, data = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

export function getErrorMessage(error) {
  if (!error) return 'Something went wrong'
  if (error instanceof ApiError) return error.message
  if (error.response?.data?.error) return error.response.data.error
  if (typeof error.message === 'string') return error.message
  return 'Something went wrong'
}

export function parseAxiosError(error) {
  const status = error.response?.status ?? 0
  const data = error.response?.data
  const message =
    data?.error ||
    (status === 401 ? 'Session expired. Please sign in again.' :
     status === 403 ? 'You do not have permission for this action.' :
     status === 404 ? 'Resource not found.' :
     status === 422 ? 'Validation failed.' :
     status >= 500 ? 'Server error. Please try again later.' :
     error.message || 'Request failed')
  return new ApiError(message, status, data)
}
