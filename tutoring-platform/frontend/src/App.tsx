import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

// Public pages
import LandingPage from '@/pages/public/LandingPage'
import AboutPage from '@/pages/public/AboutPage'
import SubjectsPage from '@/pages/public/SubjectsPage'
import ServicesPage from '@/pages/public/ServicesPage'
import BookingPage from '@/pages/public/BookingPage'
import BlogPage from '@/pages/public/BlogPage'
import ContactPage from '@/pages/public/ContactPage'

// Auth pages
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'

// Student portal
import StudentDashboard from '@/pages/student/Dashboard'
import StudentSessions from '@/pages/student/Sessions'
import StudentProgress from '@/pages/student/Progress'
import StudentResources from '@/pages/student/Resources'

// Parent portal
import ParentDashboard from '@/pages/parent/Dashboard'
import ParentFinances from '@/pages/parent/Finances'
import ParentProgress from '@/pages/parent/Progress'

// Tutor admin
import TutorDashboard from '@/pages/tutor/Dashboard'
import TutorSchedule from '@/pages/tutor/Schedule'
import TutorStudents from '@/pages/tutor/Students'
import TutorFinances from '@/pages/tutor/Finances'
import TutorAnalytics from '@/pages/tutor/Analytics'

// Layouts
import PublicLayout from '@/components/layouts/PublicLayout'
import StudentLayout from '@/components/layouts/StudentLayout'
import ParentLayout from '@/components/layouts/ParentLayout'
import TutorLayout from '@/components/layouts/TutorLayout'

// Protected routes
import ProtectedRoute from '@/components/auth/ProtectedRoute'

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#333',
          },
        }}
      />

      <Routes>
        {/* Public routes */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/subjects" element={<SubjectsPage />} />
          <Route path="/subjects/:subjectSlug" element={<SubjectsPage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/booking" element={<BookingPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/blog/:slug" element={<BlogPage />} />
          <Route path="/contact" element={<ContactPage />} />
        </Route>

        {/* Auth routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Student portal */}
        <Route
          element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <StudentLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/student" element={<StudentDashboard />} />
          <Route path="/student/sessions" element={<StudentSessions />} />
          <Route path="/student/progress" element={<StudentProgress />} />
          <Route path="/student/resources" element={<StudentResources />} />
        </Route>

        {/* Parent portal */}
        <Route
          element={
            <ProtectedRoute allowedRoles={['PARENT']}>
              <ParentLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/parent" element={<ParentDashboard />} />
          <Route path="/parent/progress" element={<ParentProgress />} />
          <Route path="/parent/finances" element={<ParentFinances />} />
        </Route>

        {/* Tutor admin */}
        <Route
          element={
            <ProtectedRoute allowedRoles={['TUTOR']}>
              <TutorLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/tutor" element={<TutorDashboard />} />
          <Route path="/tutor/schedule" element={<TutorSchedule />} />
          <Route path="/tutor/students" element={<TutorStudents />} />
          <Route path="/tutor/finances" element={<TutorFinances />} />
          <Route path="/tutor/analytics" element={<TutorAnalytics />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<div>404 - Page Not Found</div>} />
      </Routes>
    </>
  )
}

export default App
