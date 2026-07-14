import { useNavigate } from 'react-router-dom'
import { useStore } from '../store/useStore'

export default function Profile() {
  const navigate = useNavigate()
  const { user, balance, logout } = useStore()

  return (
    <div className="page">
      <div className="page-top">
        <button className="back-btn" onClick={() => navigate('/')}>
          ‹
        </button>
        <div className="page-title">👤 Профиль</div>
      </div>

      <div className="panel center" style={{ display: 'grid', gap: 8, placeItems: 'center' }}>
        <img
          className="avatar"
          style={{ width: 84, height: 84 }}
          src={user?.avatar_url || 'https://api.dicebear.com/7.x/thumbs/svg?seed=guest'}
          alt="avatar"
        />
        <div style={{ fontSize: 22, fontWeight: 900 }}>
          {user?.username || user?.first_name || `Игрок ${user?.id ?? ''}`}
        </div>
        {user?.username && user?.first_name && (
          <div className="muted">{user.first_name}</div>
        )}
        {user?.email && <div className="muted">{user.email}</div>}
        <div style={{ marginTop: 8, fontSize: 18, fontWeight: 800, color: 'var(--gold)' }}>
          {balance.toLocaleString('ru-RU', { maximumFractionDigits: 2 })} ★
        </div>
      </div>

      <button
        className="btn danger block"
        style={{ marginTop: 20 }}
        onClick={() => {
          logout()
          navigate('/login', { replace: true })
        }}
      >
        Выйти
      </button>
    </div>
  )
}
