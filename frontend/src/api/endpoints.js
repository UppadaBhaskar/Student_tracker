import api, { unwrap } from './client'

export const authApi = {
  login: (email, password) => unwrap(api.post('/auth/login', { email, password })),
  me: () => unwrap(api.get('/auth/me')),
}

export const entityApi = {
  list: () => unwrap(api.get('/entities')),
  get: (id) => unwrap(api.get(`/entities/${id}`)),
  create: (data) => unwrap(api.post('/entities', data)),
  update: (id, data) => unwrap(api.put(`/entities/${id}`, data)),
  delete: (id) => unwrap(api.delete(`/entities/${id}`)),
  dashboard: (id) => unwrap(api.get(`/entities/${id}/trainer-dashboard`)),
  analytics: (id, day = 'all') => unwrap(api.get(`/entities/${id}/analytics`, { params: { day } })),
  dailySummary: (id, day = 'all') => unwrap(api.get(`/entities/${id}/daily-summary`, { params: { day } })),
  leaderboard: (id, subjectId = 'all') =>
    unwrap(api.get(`/entities/${id}/leaderboard`, { params: { subject_id: subjectId } })),
  questionStats: (id) => unwrap(api.get(`/entities/${id}/question-statistics`)),
  export: (id, type) =>
    api.get(`/entities/${id}/export/${type}`, { responseType: 'blob' }),
  importTemplate: (type) =>
    api.get(`/entities/import-templates/${type}`, { responseType: 'blob' }),
  atRiskStudents: (id, level = 'all') =>
    unwrap(api.get(`/entities/${id}/at-risk-students`, { params: { level } })),
}

export const subjectApi = {
  list: (entityId) => unwrap(api.get(`/entities/${entityId}/subjects`)),
  create: (entityId, name) => unwrap(api.post(`/entities/${entityId}/subjects`, { name })),
  update: (id, name) => unwrap(api.put(`/entities/subjects/${id}`, { name })),
  delete: (id) => unwrap(api.delete(`/entities/subjects/${id}`)),
}

export const studentApi = {
  list: (entityId) => unwrap(api.get(`/entities/${entityId}/students`)),
  get: (id) => unwrap(api.get(`/students/${id}`)),
  create: (entityId, data) => unwrap(api.post(`/entities/${entityId}/students`, data)),
  update: (id, data) => unwrap(api.put(`/students/${id}`, data)),
  delete: (id) => unwrap(api.delete(`/students/${id}`)),
  addRemark: (id, remark) => unwrap(api.post(`/students/${id}/remarks`, { remark })),
  trends: (id) => unwrap(api.get(`/students/${id}/performance-trends`)),
  myDashboard: () => unwrap(api.get('/students/me/dashboard')),
  myTrends: () => unwrap(api.get('/students/me/performance-trends')),
  myHistory: () => unwrap(api.get('/students/me/question-history')),
  import: (entityId, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return unwrap(api.post(`/entities/${entityId}/students/import`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }))
  },
  export: (entityId) => api.get(`/entities/${entityId}/students/export`, { responseType: 'blob' }),
}

export const trackingApi = {
  getAttendance: (entityId, day) => unwrap(api.get(`/entities/${entityId}/attendance`, { params: { day } })),
  saveAttendance: (entityId, day, records) =>
    unwrap(api.put(`/entities/${entityId}/attendance`, { records }, { params: { day } })),
  getAssignments: (entityId, day) => unwrap(api.get(`/entities/${entityId}/assignments`, { params: { day } })),
  saveAssignments: (entityId, day, records) =>
    unwrap(api.put(`/entities/${entityId}/assignments`, { records }, { params: { day } })),
  getPresentations: (entityId, day) =>
    unwrap(api.get(`/entities/${entityId}/presentations`, { params: day ? { day } : {} })),
  savePresentations: (entityId, records) =>
    unwrap(api.put(`/entities/${entityId}/presentations`, { records })),
  getTestScores: (entityId) => unwrap(api.get(`/entities/${entityId}/test-scores`)),
  saveTestScores: (entityId, records) => unwrap(api.put(`/entities/${entityId}/test-scores`, { records })),
  importTestScores: (entityId, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return unwrap(api.post(`/entities/${entityId}/test-scores/import`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }))
  },
}

export const notesApi = {
  get: (entityId, day) => unwrap(api.get(`/entities/${entityId}/daily-notes`, { params: day ? { day } : {} })),
  save: (entityId, day, notes) => unwrap(api.put(`/entities/${entityId}/daily-notes/${day}`, { notes })),
}

export const questionApi = {
  list: (entityId) => unwrap(api.get(`/entities/${entityId}/questions`)),
  create: (entityId, data) => unwrap(api.post(`/entities/${entityId}/questions`, data)),
  update: (id, data) => unwrap(api.put(`/questions/${id}`, data)),
  delete: (id) => unwrap(api.delete(`/questions/${id}`)),
  reveal: (id) => unwrap(api.post(`/questions/${id}/reveal`)),
  archive: (id) => unwrap(api.post(`/questions/${id}/archive`)),
  active: () => unwrap(api.get('/questions/active')),
  complete: () => unwrap(api.post('/questions/active/complete')),
  attempts: (id, status) =>
    unwrap(api.get(`/questions/${id}/attempts`, { params: status ? { status } : {} })),
  stats: (id) => unwrap(api.get(`/questions/${id}/statistics`)),
  import: (entityId, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return unwrap(api.post('/questions/import', fd, {
      params: { entity_id: entityId },
      headers: { 'Content-Type': 'multipart/form-data' },
    }))
  },
}

export const attemptApi = {
  approve: (id, trainer_notes) =>
    unwrap(api.post(`/attempts/${id}/approve`, trainer_notes ? { trainer_notes } : {})),
  reject: (id, trainer_notes) =>
    unwrap(api.post(`/attempts/${id}/reject`, trainer_notes ? { trainer_notes } : {})),
}

export const downloadBlob = (response, fallbackName = 'export.xlsx') => {
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  const disposition = response.headers['content-disposition']
  const name = disposition?.match(/filename=(.+)/)?.[1]?.replace(/"/g, '') || fallbackName
  link.setAttribute('download', name)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
