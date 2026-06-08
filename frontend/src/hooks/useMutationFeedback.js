import { useState, useCallback } from 'react'
import { getErrorMessage } from '../api/errors'

export function useMutationFeedback() {
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const clear = useCallback(() => {
    setError(null)
    setSuccess(null)
  }, [])

  const wrap = useCallback((mutation, successMessage) => ({
    ...mutation,
    mutate: (...args) => {
      setError(null)
      setSuccess(null)
      mutation.mutate(...args, {
        onSuccess: (data, ...rest) => {
          if (successMessage) setSuccess(typeof successMessage === 'function' ? successMessage(data) : successMessage)
          mutation.options?.onSuccess?.(data, ...rest)
        },
        onError: (err) => setError(getErrorMessage(err)),
      })
    },
    mutateAsync: async (...args) => {
      setError(null)
      setSuccess(null)
      try {
        const data = await mutation.mutateAsync(...args)
        if (successMessage) setSuccess(typeof successMessage === 'function' ? successMessage(data) : successMessage)
        return data
      } catch (err) {
        setError(getErrorMessage(err))
        throw err
      }
    },
  }), [])

  return { error, success, setError, setSuccess, clear, wrap }
}
