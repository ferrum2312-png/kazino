import { Link } from 'react-router-dom'
import { useStore } from '../store/useStore'

export default function Header() {
  const { balance, user } = useStore()

  return (
    <header className="header">
      <Link to="/wallet" className="balance-pill">
        <span className="coin">★</span>
        <span>{balance.toLocaleString('ru-RU', { maximumFractionDigits: 0 })}</span>
        <span className="plus">+</span>
      </Link>
      <Link to="/profile">
        <img
          className="avatar"
          alt="profile"
          src={
            user?.avatar_url ||
            'https://api.dicebear.com/7.x/thumbs/svg?seed=guest'
          }
        />
      </Link>
    </header>
  )
}
