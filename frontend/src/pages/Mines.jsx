import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useStore } from '../store/useStore'
import Toast from '../components/Toast'

const BET_CHIPS = [10, 50, 100, 500]
const MINE_CHIPS = [1, 3, 5, 10]
const GRID = 25

export default function Mines() {
  const navigate = useNavigate()
  const { balance, refreshBalance } = useStore()
  const [bet, setBet] = useState(50)
  const [mines, setMines] = useState(3)
  const [game, setGame] = useState(null)
  const [busy, setBusy] = useState(false)
  const [toast, setToast] = useState('')

  useEffect(() => {
    refreshBalance()
    api.minesActive().then((g) => g && setGame(g)).catch(() => {})
  }, [refreshBalance])

  const revealedSet = new Set(game?.revealed || [])
  const mineSet = new Set(game?.mine_positions || [])
  const active = game?.active

  const start = async () => {
    if (bet > balance) {
      setToast('Недостаточно средств')
      return
    }
    setBusy(true)
    try {
      const g = await api.minesStart(bet, mines)
      setGame(g)
      await refreshBalance()
    } catch (e) {
      setToast(e.message)
    } finally {
      setBusy(false)
    }
  }

  const reveal = async (tile) => {
    if (!active || revealedSet.has(tile) || busy) return
    setBusy(true)
    try {
      const g = await api.minesReveal(game.game_id, tile)
      setGame(g)
      if (!g.active) {
        if (g.won) {
          setToast(`Поле очищено! +${g.payout.toFixed(2)} ★`)
        } else {
          setToast('💥 Бум! Ты попал на мину')
        }
        await refreshBalance()
      }
    } catch (e) {
      setToast(e.message)
    } finally {
      setBusy(false)
    }
  }

  const cashout = async () => {
    if (!active || !(game?.revealed?.length > 0)) return
    setBusy(true)
    try {
      const g = await api.minesCashout(game.game_id)
      setGame(g)
      setToast(`Забрал ${g.payout.toFixed(2)} ★`)
      await refreshBalance()
    } catch (e) {
      setToast(e.message)
    } finally {
      setBusy(false)
    }
  }

  const newGame = () => setGame(null)

  const currentPayout =
    game && active ? (game.bet * game.multiplier).toFixed(2) : '0.00'

  return (
    <div className="page">
      <div className="page-top">
        <button className="back-btn" onClick={() => navigate('/')}>
          ‹
        </button>
        <div className="page-title">💣 Мины</div>
      </div>

      <div className="stat-grid">
        <div className="stat">
          <div className="k">Множитель</div>
          <div className="v" style={{ color: 'var(--green)' }}>
            ×{game?.multiplier?.toFixed(2) || '1.00'}
          </div>
        </div>
        <div className="stat">
          <div className="k">Текущий выигрыш</div>
          <div className="v">{currentPayout} ★</div>
        </div>
      </div>

      <div className="mines-grid">
        {Array.from({ length: GRID }).map((_, i) => {
          const isRevealed = revealedSet.has(i)
          const isMine = !active && mineSet.has(i)
          const showGem = isRevealed && !isMine
          const showMine = isMine && (isRevealed || !active)
          return (
            <button
              key={i}
              className={`tile ${showGem ? 'gem' : ''} ${
                showMine ? 'mine' : ''
              }`}
              disabled={!active || isRevealed || busy}
              onClick={() => reveal(i)}
            >
              {showGem ? '💎' : showMine ? '💣' : ''}
            </button>
          )
        })}
      </div>

      {!active ? (
        <div className="panel">
          {game && game.won === false && (
            <div className="center" style={{ color: 'var(--danger)', marginBottom: 12, fontWeight: 700 }}>
              Раунд проигран
            </div>
          )}
          {game && game.won && (
            <div className="center" style={{ color: 'var(--green)', marginBottom: 12, fontWeight: 700 }}>
              Выигрыш {game.payout.toFixed(2)} ★
            </div>
          )}

          <div className="label">Ставка</div>
          <div className="chip-row">
            {BET_CHIPS.map((c) => (
              <button
                key={c}
                className={`chip ${bet === c ? 'active' : ''}`}
                onClick={() => setBet(c)}
              >
                {c} ★
              </button>
            ))}
          </div>

          <div className="label" style={{ marginTop: 16 }}>
            Количество мин
          </div>
          <div className="chip-row">
            {MINE_CHIPS.map((c) => (
              <button
                key={c}
                className={`chip ${mines === c ? 'active' : ''}`}
                onClick={() => setMines(c)}
              >
                {c}
              </button>
            ))}
          </div>

          <button
            className="btn green block"
            style={{ marginTop: 18 }}
            disabled={busy}
            onClick={game ? newGame : start}
          >
            {game ? 'Новая игра' : `Играть · ${bet} ★`}
          </button>
          {game && (
            <button
              className="btn green block"
              style={{ marginTop: 10 }}
              disabled={busy}
              onClick={start}
            >
              Повторить · {bet} ★
            </button>
          )}
        </div>
      ) : (
        <button
          className="btn orange block"
          disabled={busy || !(game?.revealed?.length > 0)}
          onClick={cashout}
        >
          Забрать {currentPayout} ★
        </button>
      )}

      <Toast message={toast} onClose={() => setToast('')} />
    </div>
  )
}
