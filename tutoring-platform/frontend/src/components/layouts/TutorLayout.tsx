import { Outlet } from 'react-router-dom'

export default function TutorLayout() {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar navigation */}
      <main className="flex-grow p-6">
        <Outlet />
      </main>
    </div>
  )
}
