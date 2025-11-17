import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Pages (to be implemented)
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Accounts from './pages/Accounts'
import Transactions from './pages/Transactions'
import Budgets from './pages/Budgets'
import Investments from './pages/Investments'
import Goals from './pages/Goals'
import Forecasting from './pages/Forecasting'
import Reports from './pages/Reports'
import Settings from './pages/Settings'

// Layout
import Layout from './components/Layout'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
      <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />

      {/* Protected routes */}
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/accounts" element={<Accounts />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/budgets" element={<Budgets />} />
        <Route path="/investments" element={<Investments />} />
        <Route path="/goals" element={<Goals />} />
        <Route path="/forecasting" element={<Forecasting />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">404</h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">Page not found</p>
          <a href="/dashboard" className="text-primary-600 hover:text-primary-700 font-medium">
            Go to Dashboard
          </a>
        </div>
      </div>} />
    </Routes>
  )
}

export default App
