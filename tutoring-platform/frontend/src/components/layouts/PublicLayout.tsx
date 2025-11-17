import { Outlet } from 'react-router-dom'

export default function PublicLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header/Navigation will go here */}
      <main className="flex-grow">
        <Outlet />
      </main>
      {/* Footer will go here */}
    </div>
  )
}
