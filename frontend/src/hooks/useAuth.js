import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { authApi } from '../api/endpoints'
import { queryKeys } from '../api/queryKeys'

export function useAuthSession(enabled = true) {
  return useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: authApi.me,
    enabled: enabled && !!localStorage.getItem('token'),
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}

export function useLoginMutation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ email, password }) => authApi.login(email, password),
    onSuccess: (data) => {
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      qc.setQueryData(queryKeys.auth.me, data.user)
    },
  })
}

export function useLogout() {
  const qc = useQueryClient()
  return () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('selectedEntityId')
    qc.clear()
  }
}
