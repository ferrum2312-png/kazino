import { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useStore } from './store/useStore'
import BottomNav from './components/BottomNav'
import Home from './pages/Home'
import Login from './pages/Login'
import Crash from './pages/Crash'
import Mines from './pages/Mines'
import Wallet from './pages/Wallet'
import Profile from './pages/Profile'
import Cases from './pages/Cases'
import GamePlaceholder from './pages/GamePlaceholder'

function RequireAuth({ children }) {
  const { user, loading } = useStore()
  const location = useLocation()
  if (loading) return <div className="spinner" />
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

export default function App() {
  const { bootstrap, user } = useStore()
  const location = useLocation()

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.ready()
      tg.expand?.()
      tg.setHeaderColor?.('#070708')
      tg.setBackgroundColor?.('#070708')
    }
    bootstrap()
  }, [bootstrap])

  const showNav = user && location.pathname !== '/login'

  return (
    <>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <Home />
            </RequireAuth>
          }
        />
        <Route
          path="/game/crash"
          element={
            <RequireAuth>
              <Crash />
            </RequireAuth>
          }
        />
        <Route
          path="/game/mines"
          element={
            <RequireAuth>
              <Mines />
            </RequireAuth>
          }
        />
        <Route
          path="/game/:slug"
          element={
            <RequireAuth>
              <GamePlaceholder />
            </RequireAuth>
          }
        />
        <Route
          path="/cases"
          element={
            <RequireAuth>
              <Cases />
            </RequireAuth>
          }
        />
        <Route
          path="/wallet"
          element={
            <RequireAuth>
              <Wallet />
            </RequireAuth>
          }
        />
        <Route
          path="/profile"
          element={
            <RequireAuth>
              <Profile />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      {showNav && <BottomNav />}
    </>
  )
}
