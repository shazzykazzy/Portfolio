import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'

interface ProtectedRouteProps {
  children: ReactNode
  allowedRoles: string[]
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  // TODO: Implement actual authentication check
  const isAuthenticated = false // Replace with actual auth state
  const userRole = 'STUDENT' // Replace with actual user role

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!allowedRoles.includes(userRole)) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
