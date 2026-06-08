import { useQuery } from '@tanstack/react-query'
import { entityApi, studentApi } from '../api/endpoints'
import { queryKeys } from '../api/queryKeys'

export function useStudentDashboard(options = {}) {
  return useQuery({
    queryKey: queryKeys.students.meDashboard,
    queryFn: studentApi.myDashboard,
    ...options,
  })
}

export function useMyTrends(options = {}) {
  return useQuery({
    queryKey: queryKeys.students.meTrends,
    queryFn: studentApi.myTrends,
    ...options,
  })
}

export function useQuestionHistory(options = {}) {
  return useQuery({
    queryKey: queryKeys.students.meHistory,
    queryFn: studentApi.myHistory,
    ...options,
  })
}

export function useStudentLeaderboard(entityId, subjectId = 'all', options = {}) {
  return useQuery({
    queryKey: queryKeys.entities.leaderboard(entityId, subjectId),
    queryFn: () => entityApi.leaderboard(entityId, subjectId),
    enabled: !!entityId,
    ...options,
  })
}
