import { useNavigate } from 'react-router-dom'

const EMOJI = {
  raffles: '🎁',
  'ralph-arena': '🕹️',
  duel: '⚔️',
  crash: '🚀',
  mines: '💣',
}

export default function GameCard({ game }) {
  const navigate = useNavigate()

  const handleClick = () => {
    if (game.playable) navigate(`/game/${game.slug}`)
  }

  return (
    <button
      className="game-card"
      onClick={handleClick}
      style={{ opacity: game.playable ? 1 : 0.92 }}
    >
      {game.live && <span className="badge-live">LIVE</span>}
      <span
        className="glow"
        style={{ background: game.accent || '#8a5cff' }}
      />
      <div>
        <div className="title">{game.title}</div>
        <div className="subtitle">
          {game.playable ? game.subtitle : 'Скоро'}
        </div>
      </div>
      <span className="emoji">{EMOJI[game.slug] || '🎰'}</span>
    </button>
  )
}
