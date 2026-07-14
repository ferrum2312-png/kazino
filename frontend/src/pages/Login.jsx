import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../store/useStore'

export default function Login() {
  const navigate = useNavigate()
  const { login, register, loginWithTelegram, inTelegram } = useStore()
  const [mode, setMode] = useState('login')
  const [showDev, setShowDev] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const retryTelegram = async () => {
    setError('')
    setBusy(true)
    try {
      await loginWithTelegram()
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const submitDev = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (mode === 'login') await login(username, password)
      else await register(username, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="app" style={{ paddingTop: 60 }}>
      <div className="banner" style={{ marginBottom: 28 }}>
        <span className="glow-777">777</span>
        <h1>KAZINO</h1>
        <p>Играй прямо в Telegram</p>
      </div>

      {inTelegram ? (
        <div className="panel center" style={{ display: 'grid', gap: 14 }}>
          <div style={{ fontSize: 40 }}>🔐</div>
          <div style={{ fontWeight: 700 }}>Авторизация через Telegram…</div>
          {error && (
            <div style={{ color: 'var(--danger)', fontSize: 14 }}>{error}</div>
          )}
          <button className="btn block" disabled={busy} onClick={retryTelegram}>
            {busy ? '...' : 'Повторить'}
          </button>
        </div>
      ) : (
        <div className="panel center" style={{ display: 'grid', gap: 12 }}>
          <div style={{ fontSize: 44 }}>📱</div>
          <div style={{ fontWeight: 800, fontSize: 18 }}>
            Открой приложение в Telegram
          </div>
          <p className="muted" style={{ fontSize: 14 }}>
            Вход происходит автоматически через твой Telegram‑аккаунт. Открой
            мини‑приложение через бота, а не в обычном браузере.
          </p>

          <button
            className="btn ghost"
            style={{ marginTop: 4 }}
            onClick={() => setShowDev((v) => !v)}
          >
            {showDev ? 'Скрыть' : 'Тестовый вход (для разработки)'}
          </button>

          {showDev && (
            <form onSubmit={submitDev} style={{ display: 'grid', gap: 12, marginTop: 6 }}>
              <input
                className="input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Имя пользователя"
                autoCapitalize="none"
                required
              />
              <input
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Пароль"
                required
              />
              {error && (
                <div style={{ color: 'var(--danger)', fontSize: 14 }}>{error}</div>
              )}
              <button className="btn block" disabled={busy}>
                {busy ? '...' : mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
              </button>
              <button
                className="btn ghost"
                type="button"
                onClick={() => {
                  setMode(mode === 'login' ? 'register' : 'login')
                  setError('')
                }}
              >
                {mode === 'login' ? 'Создать тестовый аккаунт' : 'У меня есть аккаунт'}
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  )
}
