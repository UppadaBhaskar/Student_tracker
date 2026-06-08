import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { trackingApi, notesApi } from '../api/endpoints'
import { queryKeys } from '../api/queryKeys'

export function useAttendance(entityId, day, options = {}) {
  return useQuery({
    queryKey: queryKeys.tracking.attendance(entityId, day),
    queryFn: () => trackingApi.getAttendance(entityId, day),
    enabled: !!entityId && !!day,
    ...options,
  })
}

export function useSaveAttendance(entityId, day) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (records) => trackingApi.saveAttendance(entityId, day, records),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.tracking.attendance(entityId, day) })
      qc.invalidateQueries({ queryKey: queryKeys.entities.dashboard(entityId) })
    },
  })
}

export function useAssignments(entityId, day, options = {}) {
  return useQuery({
    queryKey: queryKeys.tracking.assignments(entityId, day),
    queryFn: () => trackingApi.getAssignments(entityId, day),
    enabled: !!entityId && !!day,
    ...options,
  })
}

export function useSaveAssignments(entityId, day) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (records) => trackingApi.saveAssignments(entityId, day, records),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.tracking.assignments(entityId, day) })
      qc.invalidateQueries({ queryKey: queryKeys.entities.dashboard(entityId) })
    },
  })
}

export function usePresentations(entityId, day, options = {}) {
  return useQuery({
    queryKey: queryKeys.tracking.presentations(entityId, day),
    queryFn: () => trackingApi.getPresentations(entityId, day),
    enabled: !!entityId,
    ...options,
  })
}

export function useSavePresentations(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (records) => trackingApi.savePresentations(entityId, records),
    onSuccess: (_, records) => {
      const day = records?.[0]?.day
      if (day) qc.invalidateQueries({ queryKey: queryKeys.tracking.presentations(entityId, day) })
    },
  })
}

export function useTestScores(entityId, options = {}) {
  return useQuery({
    queryKey: queryKeys.tracking.testScores(entityId),
    queryFn: () => trackingApi.getTestScores(entityId),
    enabled: !!entityId,
    ...options,
  })
}

export function useSaveTestScores(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (records) => trackingApi.saveTestScores(entityId, records),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.tracking.testScores(entityId) }),
  })
}

export function useImportTestScores(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file) => trackingApi.importTestScores(entityId, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.tracking.testScores(entityId) }),
  })
}

export function useDailyNotes(entityId, day, options = {}) {
  return useQuery({
    queryKey: queryKeys.notes.day(entityId, day),
    queryFn: () => notesApi.get(entityId, day),
    enabled: !!entityId && !!day,
    select: (data) => data?.[0]?.notes ?? '',
    ...options,
  })
}

export function useSaveDailyNotes(entityId, day) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (notes) => notesApi.save(entityId, day, notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.notes.day(entityId, day) }),
  })
}
