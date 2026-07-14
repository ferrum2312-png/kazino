import { useNavigate } from 'react-router-dom'
import { useI18n, gameTitles } from '../i18n'

const EMOJI = {
  raffles: '🎁',
  'ralph-arena': '🕹️',
  duel: '⚔️',
  crash: '🚀',
  mines: '💣',
}

const SUB_KEY = {
  crash: 'sub_crash',
  mines: 'sub_mines',
  duel: 'sub_duel',
  'ralph-arena': 'sub_arena',
}

export default function GameCard({ game }) {
  const navigate = useNavigate()
  const { t, lang } = useI18n()

  const title = gameTitles[game.slug]?.[lang] || game.title
  const subtitle = SUB_KEY[game.slug] ? t(SUB_KEY[game.slug]) : game.subtitle

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
        <div className="title">{title}</div>
        <div className="subtitle">
          {game.playable ? subtitle : t('soon')}
        </div>
      </div>
      <span className="emoji">{EMOJI[game.slug] || '🎰'}</span>
    </button>
  )
}
