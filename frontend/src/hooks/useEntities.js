import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { entityApi } from '../api/endpoints'
import { queryKeys } from '../api/queryKeys'

export function useEntities(options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.all,
    queryFn: entityApi.list,
    ...options,
  })
}

export function useEntity(id, options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.detail(id),
    queryFn: () => entityApi.get(id),
    enabled: !!id,
    ...options,
  })
}

export function useTrainerDashboard(entityId, options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.dashboard(entityId),
    queryFn: () => entityApi.dashboard(entityId),
    enabled: !!entityId,
    ...options,
  })
}

export function useCreateEntity() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: entityApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.entities.all }),
  })
}

export function useUpdateEntity() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => entityApi.update(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.entities.all })
      qc.invalidateQueries({ queryKey: queryKeys.entities.detail(id) })
    },
  })
}

export function useDeleteEntity() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: entityApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.entities.all }),
  })
}

export function useAnalytics(entityId, day = 'all', options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.analytics(entityId, day),
    queryFn: () => entityApi.analytics(entityId, day),
    enabled: !!entityId,
    ...options,
  })
}

export function useDailySummary(entityId, day = 'all', options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.dailySummary(entityId, day),
    queryFn: () => entityApi.dailySummary(entityId, day),
    enabled: !!entityId,
    ...options,
  })
}

export function useLeaderboard(entityId, subjectId = 'all', options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.leaderboard(entityId, subjectId),
    queryFn: () => entityApi.leaderboard(entityId, subjectId),
    enabled: !!entityId,
    ...options,
  })
}

export function useQuestionStatistics(entityId, options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.questionStats(entityId),
    queryFn: () => entityApi.questionStats(entityId),
    enabled: !!entityId,
    ...options,
  })
}

export function useExportEntity() {
  return useMutation({
    mutationFn: ({ entityId, type }) => entityApi.export(entityId, type),
  })
}

export function useImportTemplate() {
  return useMutation({
    mutationFn: (type) => entityApi.importTemplate(type),
  })
}

export function useAtRiskStudents(entityId, level = 'all', options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.atRisk(entityId, level),
    queryFn: () => entityApi.atRiskStudents(entityId, level),
    enabled: !!entityId,
    ...options,
  })
}
