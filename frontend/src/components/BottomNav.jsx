import { Link, useLocation } from 'react-router-dom'

const ITEMS = [
  { to: '/', ic: '🏠', label: 'Главная' },
  { to: '/game/crash', ic: '🚀', label: 'Краш' },
  { to: '/game/mines', ic: '💣', label: 'Мины' },
  { to: '/wallet', ic: '💰', label: 'Кошелёк' },
  { to: '/profile', ic: '👤', label: 'Профиль' },
]

export default function BottomNav() {
  const { pathname } = useLocation()
  return (
    <nav className="bottom-nav">
      {ITEMS.map((it) => {
        const active =
          it.to === '/' ? pathname === '/' : pathname.startsWith(it.to)
        return (
          <Link
            key={it.to}
            to={it.to}
            className={`nav-item ${active ? 'active' : ''}`}
          >
            <span className="ic">{it.ic}</span>
            <span>{it.label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
