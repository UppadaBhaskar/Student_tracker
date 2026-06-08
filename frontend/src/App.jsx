import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './context/AuthContext'
import { EntityProvider } from './context/EntityContext'
import { ProtectedRoute } from './components/layout/ProtectedRoute'
import TrainerLayout from './components/layout/TrainerLayout'
import StudentLayout from './components/layout/StudentLayout'
import LoginPage from './pages/auth/LoginPage'
import TrainerDashboard from './pages/trainer/TrainerDashboard'
import EntityListPage from './pages/trainer/EntityListPage'
import EntityFormPage from './pages/trainer/EntityFormPage'
import SubjectManagementPage from './pages/trainer/SubjectManagementPage'
import StudentListPage from './pages/trainer/StudentListPage'
import StudentFormPage from './pages/trainer/StudentFormPage'
import StudentProfilePage from './pages/trainer/StudentProfilePage'
import { AttendancePage, AssignmentsPage } from './pages/trainer/TrackingPages'
import PresentationsPage from './pages/trainer/PresentationsPage'
import TestScoresPage from './pages/trainer/TestScoresPage'
import DailyNotesPage from './pages/trainer/DailyNotesPage'
import QuestionListPage from './pages/trainer/QuestionListPage'
import QuestionFormPage from './pages/trainer/QuestionFormPage'
import ActiveQuestionPage from './pages/trainer/ActiveQuestionPage'
import VerificationQueuePage from './pages/trainer/VerificationQueuePage'
import QuestionStatisticsPage from './pages/trainer/QuestionStatisticsPage'
import LeaderboardPage from './pages/trainer/LeaderboardPage'
import AnalyticsPage from './pages/trainer/AnalyticsPage'
import DailySummaryPage from './pages/trainer/DailySummaryPage'
import ImportExportPage from './pages/trainer/ImportExportPage'
import StudentDashboard from './pages/student/StudentDashboard'
import StudentActiveQuestionPage from './pages/student/StudentActiveQuestionPage'
import QuestionHistoryPage from './pages/student/QuestionHistoryPage'
import StudentLeaderboardPage from './pages/student/StudentLeaderboardPage'
import ProfilePage from './pages/student/ProfilePage'
import { getErrorMessage } from './api/errors'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (count, error) => count < 1 && error?.status !== 401 && error?.status !== 403,
      staleTime: 30 * 1000,
      refetchOnWindowFocus: true,
    },
    mutations: {
      onError: (error) => {
        console.error('[API]', getErrorMessage(error))
      },
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<Navigate to="/login" replace />} />

            <Route element={<ProtectedRoute role="trainer" />}>
              <Route element={<EntityProvider><TrainerLayout /></EntityProvider>}>
                <Route path="/trainer/dashboard" element={<TrainerDashboard />} />
                <Route path="/trainer/entities" element={<EntityListPage />} />
                <Route path="/trainer/entities/new" element={<EntityFormPage />} />
                <Route path="/trainer/entities/:id/edit" element={<EntityFormPage />} />
                <Route path="/trainer/entities/:id/subjects" element={<SubjectManagementPage />} />
                <Route path="/trainer/entities/:id/students" element={<StudentListPage />} />
                <Route path="/trainer/entities/:id/students/new" element={<StudentFormPage />} />
                <Route path="/trainer/entities/:id/students/:sid" element={<StudentProfilePage />} />
                <Route path="/trainer/entities/:id/students/:sid/edit" element={<StudentFormPage />} />
                <Route path="/trainer/entities/:id/attendance" element={<AttendancePage />} />
                <Route path="/trainer/entities/:id/assignments" element={<AssignmentsPage />} />
                <Route path="/trainer/entities/:id/presentations" element={<PresentationsPage />} />
                <Route path="/trainer/entities/:id/test-scores" element={<TestScoresPage />} />
                <Route path="/trainer/entities/:id/daily-notes" element={<DailyNotesPage />} />
                <Route path="/trainer/entities/:id/questions" element={<QuestionListPage />} />
                <Route path="/trainer/entities/:id/questions/new" element={<QuestionFormPage />} />
                <Route path="/trainer/entities/:id/questions/:qid/edit" element={<QuestionFormPage />} />
                <Route path="/trainer/entities/:id/question-statistics" element={<QuestionStatisticsPage />} />
                <Route path="/trainer/entities/:id/leaderboard" element={<LeaderboardPage />} />
                <Route path="/trainer/entities/:id/analytics" element={<AnalyticsPage />} />
                <Route path="/trainer/entities/:id/daily-summary" element={<DailySummaryPage />} />
                <Route path="/trainer/entities/:id/import-export" element={<ImportExportPage />} />
                <Route path="/trainer/questions/active" element={<ActiveQuestionPage />} />
                <Route path="/trainer/questions/verification" element={<VerificationQueuePage />} />
              </Route>
            </Route>

            <Route element={<ProtectedRoute role="student" />}>
              <Route element={<StudentLayout />}>
                <Route path="/student/dashboard" element={<StudentDashboard />} />
                <Route path="/student/active-question" element={<StudentActiveQuestionPage />} />
                <Route path="/student/question-history" element={<QuestionHistoryPage />} />
                <Route path="/student/leaderboard" element={<StudentLeaderboardPage />} />
                <Route path="/student/profile" element={<ProfilePage />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
