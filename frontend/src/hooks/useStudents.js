import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { studentApi } from '../api/endpoints'
import { queryKeys } from '../api/queryKeys'

export function useStudents(entityId, options = {}) {
  return useQuery({
    queryKey: queryKeys.students.list(entityId),
    queryFn: () => studentApi.list(entityId),
    enabled: !!entityId,
    ...options,
  })
}

export function useStudent(id, options = {}) {
  return useQuery({
    queryKey: queryKeys.students.detail(id),
    queryFn: () => studentApi.get(id),
    enabled: !!id,
    ...options,
  })
}

export function useStudentTrends(id, options = {}) {
  return useQuery({
    queryKey: queryKeys.students.trends(id),
    queryFn: () => studentApi.trends(id),
    enabled: !!id,
    ...options,
  })
}

export function useCreateStudent(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => studentApi.create(entityId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.students.list(entityId) })
      qc.invalidateQueries({ queryKey: queryKeys.entities.dashboard(entityId) })
    },
  })
}

export function useUpdateStudent(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => studentApi.update(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.students.list(entityId) })
      qc.invalidateQueries({ queryKey: queryKeys.students.detail(id) })
    },
  })
}

export function useDeleteStudent(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: studentApi.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.students.list(entityId) })
      qc.invalidateQueries({ queryKey: queryKeys.entities.dashboard(entityId) })
    },
  })
}

export function useAddRemark(studentId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (remark) => studentApi.addRemark(studentId, remark),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.students.detail(studentId) }),
  })
}

export function useImportStudents(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file) => studentApi.import(entityId, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.students.list(entityId) }),
  })
}
