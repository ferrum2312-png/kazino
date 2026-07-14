import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, crashSocketUrl, getToken } from '../api/client'
import { useStore } from '../store/useStore'
import Toast from '../components/Toast'

const BET_CHIPS = [10, 50, 100, 500]

function histClass(v) {
  if (v < 2) return 'low'
  if (v < 10) return 'mid'
  return 'high'
}

export default function Crash() {
  const navigate = useNavigate()
  const { balance, refreshBalance, setBalance } = useStore()
  const wsRef = useRef(null)
  const reconnectRef = useRef(null)

  const [phase, setPhase] = useState('connecting') // connecting|betting|running|crashed
  const [multiplier, setMultiplier] = useState(1.0)
  const [timeLeft, setTimeLeft] = useState(0)
  const [players, setPlayers] = useState([])
  const [history, setHistory] = useState([])
  const [bet, setBet] = useState(50)
  const [autoCashout, setAutoCashout] = useState('')
  const [myBet, setMyBet] = useState(null) // {amount, cashedOut}
  const [toast, setToast] = useState('')

  useEffect(() => {
    api.crashHistory().then((h) => setHistory(h.history)).catch(() => {})
    refreshBalance()
    connect()
    return () => {
      clearTimeout(reconnectRef.current)
      wsRef.current?.close()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const connect = () => {
    const ws = new WebSocket(crashSocketUrl())
    wsRef.current = ws

    ws.onopen = () => {
      ws.send(JSON.stringify({ action: 'auth', token: getToken() }))
    }

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      switch (msg.type) {
        case 'state':
          setPhase(msg.status === 'crashed' ? 'crashed' : msg.status || 'betting')
          setMultiplier(msg.multiplier || 1.0)
          setPlayers(msg.players || [])
          if (msg.status === 'betting' && msg.time_left != null)
            setTimeLeft(msg.time_left)
          break
        case 'betting':
          setPhase('betting')
          setMultiplier(1.0)
          setMyBet(null)
          setPlayers([])
          setTimeLeft(msg.duration)
          break
        case 'running':
          setPhase('running')
          break
        case 'tick':
          setMultiplier(msg.multiplier)
          break
        case 'crashed':
          setPhase('crashed')
          setMultiplier(msg.crash_point)
          setHistory((h) => [msg.crash_point, ...h].slice(0, 30))
          setMyBet((mb) =>
            mb && mb.cashedOut == null ? { ...mb, lost: true } : mb
          )
          break
        case 'players':
          setPlayers(msg.players)
          break
        case 'bet_ok':
          setMyBet({ amount: msg.amount, cashedOut: null })
          setBalance(msg.balance)
          setToast(`Ставка ${msg.amount} ★ принята`)
          break
        case 'cashout_ok':
          setMyBet((mb) => (mb ? { ...mb, cashedOut: msg.multiplier } : mb))
          setToast(`Забрал ×${msg.multiplier} = ${msg.payout.toFixed(2)} ★`)
          refreshBalance()
          break
        case 'error':
          setToast(msg.message)
          break
        default:
          break
      }
    }

    ws.onclose = () => {
      reconnectRef.current = setTimeout(connect, 1500)
    }
    ws.onerror = () => ws.close()
  }

  // betting countdown
  useEffect(() => {
    if (phase !== 'betting' || timeLeft <= 0) return
    const t = setInterval(() => setTimeLeft((s) => Math.max(0, s - 0.1)), 100)
    return () => clearInterval(t)
  }, [phase, timeLeft])

  const placeBet = () => {
    if (bet > balance) {
      setToast('Недостаточно средств')
      return
    }
    const auto = autoCashout ? parseFloat(autoCashout) : null
    wsRef.current?.send(
      JSON.stringify({ action: 'bet', amount: bet, auto_cashout: auto })
    )
  }

  const cashOut = () => {
    wsRef.current?.send(JSON.stringify({ action: 'cashout' }))
  }

  const canBet = phase === 'betting' && !myBet
  const canCashout =
    phase === 'running' && myBet && myBet.cashedOut == null && !myBet.lost

  const multClass =
    phase === 'crashed' ? 'crashed' : phase === 'running' ? 'running' : 'betting'

  return (
    <div className="page">
      <div className="page-top">
        <button className="back-btn" onClick={() => navigate('/')}>
          ‹
        </button>
        <div className="page-title">🚀 Краш</div>
      </div>

      <div className="history-strip">
        {history.map((v, i) => (
          <span key={i} className={`hchip ${histClass(v)}`}>
            ×{v.toFixed(2)}
          </span>
        ))}
      </div>

      <div className="crash-stage">
        <div className="crash-status">
          {phase === 'connecting' && 'Подключение...'}
          {phase === 'betting' && `Приём ставок · ${timeLeft.toFixed(1)}с`}
          {phase === 'running' && 'Полёт!'}
          {phase === 'crashed' && 'Взрыв!'}
        </div>
        <div className={`crash-multiplier ${multClass}`}>
          ×{multiplier.toFixed(2)}
        </div>
      </div>

      {myBet && (
        <div
          className="panel center"
          style={{ marginTop: 12, fontWeight: 700 }}
        >
          {myBet.cashedOut
            ? `✅ Забрал ×${myBet.cashedOut.toFixed(2)}`
            : myBet.lost
            ? `❌ Проигрыш ${myBet.amount} ★`
            : `Ставка в игре: ${myBet.amount} ★`}
        </div>
      )}

      <div style={{ marginTop: 14 }}>
        {canCashout ? (
          <button className="btn orange block" onClick={cashOut}>
            Забрать ×{multiplier.toFixed(2)} = {(myBet.amount * multiplier).toFixed(2)} ★
          </button>
        ) : (
          <div className="panel">
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
            <div className="label" style={{ marginTop: 14 }}>
              Авто-вывод (×), необязательно
            </div>
            <input
              className="input"
              type="number"
              step="0.1"
              min="1.1"
              placeholder="напр. 2.0"
              value={autoCashout}
              onChange={(e) => setAutoCashout(e.target.value)}
            />
            <button
              className="btn green block"
              style={{ marginTop: 14 }}
              disabled={!canBet}
              onClick={placeBet}
            >
              {myBet
                ? 'Ставка принята'
                : phase === 'betting'
                ? `Поставить ${bet} ★`
                : 'Ожидание раунда...'}
            </button>
          </div>
        )}
      </div>

      <div style={{ marginTop: 18 }}>
        <div className="label">Игроки ({players.length})</div>
        <div className="players-list">
          {players.length === 0 && (
            <div className="muted center" style={{ padding: 16 }}>
              Пока никто не сделал ставку
            </div>
          )}
          {players.map((p, i) => (
            <div className="player-row" key={i}>
              <span>{p.username}</span>
              <span>
                {p.amount} ★{' '}
                {p.cashed_out ? (
                  <span className="out">×{p.cashed_out.toFixed(2)}</span>
                ) : (
                  ''
                )}
              </span>
            </div>
          ))}
        </div>
      </div>

      <Toast message={toast} onClose={() => setToast('')} />
    </div>
  )
}
