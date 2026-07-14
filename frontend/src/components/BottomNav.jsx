import { Link, useLocation } from 'react-router-dom'

const CasesIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2.5" y="7" width="19" height="13" rx="2.5" />
    <path d="M8 7V5.5A2.5 2.5 0 0 1 10.5 3h3A2.5 2.5 0 0 1 16 5.5V7" />
    <path d="M2.5 12h19" />
  </svg>
)

const HomeIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round">
    <path d="M12 2 21 7 21 17 12 22 3 17 3 7Z" />
    <path d="M12 9 15 12 12 15 9 12Z" />
  </svg>
)

const ProfileIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="9.5" />
    <circle cx="12" cy="10" r="3" />
    <path d="M6.3 18.7a5.9 5.9 0 0 1 11.4 0" />
  </svg>
)

const ITEMS = [
  { to: '/cases', label: 'Кейсы', Icon: CasesIcon },
  { to: '/', label: 'Главная', Icon: HomeIcon },
  { to: '/profile', label: 'Профиль', Icon: ProfileIcon },
]

export default function BottomNav() {
  const { pathname } = useLocation()
  return (
    <nav className="bottom-nav">
      {ITEMS.map(({ to, label, Icon }) => {
        const active =
          to === '/'
            ? pathname === '/' || pathname.startsWith('/game')
            : pathname.startsWith(to)
        return (
          <Link key={to} to={to} className={`nav-item ${active ? 'active' : ''}`}>
            <Icon />
            <span>{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
