import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import WorkoutsPage from './pages/WorkoutsPage'
import WorkoutDetailPage from './pages/WorkoutDetailPage'
import NewWorkoutPage from './pages/NewWorkoutPage'
import WearablesPage from './pages/WearablesPage'
import GymsPage from './pages/GymsPage'
import GymDetailPage from './pages/GymDetailPage'
import BasketballPage from './pages/BasketballPage'
import ProfilePage from './pages/ProfilePage'
import ExplorePage from './pages/ExplorePage'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading-page"><div className="spinner" /></div>
  if (!user) return <Navigate to="/login" />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<DashboardPage />} />
        <Route path="workouts" element={<WorkoutsPage />} />
        <Route path="workouts/new" element={<NewWorkoutPage />} />
        <Route path="workouts/:id" element={<WorkoutDetailPage />} />
        <Route path="wearables" element={<WearablesPage />} />
        <Route path="gyms" element={<GymsPage />} />
        <Route path="gyms/:id" element={<GymDetailPage />} />
        <Route path="explore" element={<ExplorePage />} />
        <Route path="basketball" element={<BasketballPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>
    </Routes>
  )
}
