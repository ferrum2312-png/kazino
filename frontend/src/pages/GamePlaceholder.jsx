import { useNavigate, useParams } from 'react-router-dom'

const TITLES = {
  raffles: '🎁 Розыгрыши',
  'ralph-arena': '🕹️ Vavada Арена',
  duel: '⚔️ ПВП Дуэль',
}

export default function GamePlaceholder() {
  const { slug } = useParams()
  const navigate = useNavigate()

  return (
    <div className="page">
      <div className="page-top">
        <button className="back-btn" onClick={() => navigate('/')}>
          ‹
        </button>
        <div className="page-title">{TITLES[slug] || 'Игра'}</div>
      </div>

      <div className="panel center" style={{ padding: 40 }}>
        <div style={{ fontSize: 60, marginBottom: 12 }}>🚧</div>
        <div style={{ fontSize: 20, fontWeight: 800 }}>Скоро в игре</div>
        <p className="muted" style={{ marginTop: 8 }}>
          Этот режим ещё в разработке. Загляни в «Краш» или «Мины» —
          они уже работают!
        </p>
        <button
          className="btn block"
          style={{ marginTop: 20 }}
          onClick={() => navigate('/game/crash')}
        >
          Играть в Краш
        </button>
      </div>
    </div>
  )
}
