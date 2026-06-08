export const queryKeys = {
  auth: {
    me: ['auth', 'me'],
  },
  entities: {
    all: ['entities'],
    detail: (id) => ['entities', id],
    dashboard: (id) => ['entities', id, 'dashboard'],
    analytics: (id, day) => ['entities', id, 'analytics', day],
    dailySummary: (id, day) => ['entities', id, 'daily-summary', day],
    leaderboard: (id, subjectId) => ['entities', id, 'leaderboard', subjectId],
    questionStats: (id) => ['entities', id, 'question-stats'],
    atRisk: (id, level) => ['entities', id, 'at-risk', level],
  },
  subjects: {
    list: (entityId) => ['subjects', entityId],
  },
  students: {
    list: (entityId) => ['students', entityId],
    detail: (id) => ['students', id],
    trends: (id) => ['students', id, 'trends'],
    meDashboard: ['students', 'me', 'dashboard'],
    meTrends: ['students', 'me', 'trends'],
    meHistory: ['students', 'me', 'history'],
  },
  tracking: {
    attendance: (entityId, day) => ['attendance', entityId, day],
    assignments: (entityId, day) => ['assignments', entityId, day],
    presentations: (entityId, day) => ['presentations', entityId, day],
    testScores: (entityId) => ['test-scores', entityId],
  },
  notes: {
    day: (entityId, day) => ['daily-notes', entityId, day],
  },
  questions: {
    list: (entityId) => ['questions', entityId],
    active: ['questions', 'active'],
    attempts: (id, status) => ['questions', id, 'attempts', status ?? 'all'],
    stats: (id) => ['questions', id, 'stats'],
  },
}
