import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { subjectApi } from '../api/endpoints'
import { queryKeys } from '../api/queryKeys'

export function useSubjects(entityId, options = {}) {
  return useQuery({
    queryKey: queryKeys.subjects.list(entityId),
    queryFn: () => subjectApi.list(entityId),
    enabled: !!entityId,
    ...options,
  })
}

export function useCreateSubject(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (name) => subjectApi.create(entityId, name),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.subjects.list(entityId) }),
  })
}

export function useUpdateSubject(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, name }) => subjectApi.update(id, name),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.subjects.list(entityId) }),
  })
}

export function useDeleteSubject(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: subjectApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.subjects.list(entityId) }),
  })
}
