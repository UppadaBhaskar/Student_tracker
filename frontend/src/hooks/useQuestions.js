import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { questionApi, attemptApi } from '../api/endpoints'
import { queryKeys } from '../api/queryKeys'

export function useQuestions(entityId, options = {}) {
  return useQuery({
    queryKey: queryKeys.questions.list(entityId),
    queryFn: () => questionApi.list(entityId),
    enabled: !!entityId,
    ...options,
  })
}

export function useActiveQuestion(options = {}) {
  return useQuery({
    queryKey: queryKeys.questions.active,
    queryFn: questionApi.active,
    refetchInterval: options.refetchInterval ?? false,
    ...options,
  })
}

export function useQuestionAttempts(questionId, status, options = {}) {
  return useQuery({
    queryKey: queryKeys.questions.attempts(questionId, status),
    queryFn: () => questionApi.attempts(questionId, status),
    enabled: !!questionId,
    refetchInterval: options.refetchInterval ?? false,
    ...options,
  })
}

export function useCreateQuestion(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => questionApi.create(entityId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.questions.list(entityId) }),
  })
}

export function useUpdateQuestion(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => questionApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.questions.list(entityId) })
      qc.invalidateQueries({ queryKey: queryKeys.questions.active })
    },
  })
}

export function useDeleteQuestion(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: questionApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.questions.list(entityId) }),
  })
}

export function useRevealQuestion(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: questionApi.reveal,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.questions.list(entityId) })
      qc.invalidateQueries({ queryKey: queryKeys.questions.active })
    },
  })
}

export function useArchiveQuestion(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: questionApi.archive,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.questions.list(entityId) })
      qc.invalidateQueries({ queryKey: queryKeys.questions.active })
    },
  })
}

export function useCompleteQuestion() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: questionApi.complete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.questions.active })
      qc.invalidateQueries({ queryKey: queryKeys.students.meDashboard })
      qc.invalidateQueries({ queryKey: queryKeys.students.meHistory })
    },
  })
}

export function useApproveAttempt() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, trainer_notes }) => attemptApi.approve(id, trainer_notes),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['questions'] })
      qc.invalidateQueries({ queryKey: queryKeys.entities.all })
    },
  })
}

export function useRejectAttempt() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, trainer_notes }) => attemptApi.reject(id, trainer_notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['questions'] }),
  })
}

export function useImportQuestions(entityId) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file) => questionApi.import(entityId, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.questions.list(entityId) }),
  })
}
