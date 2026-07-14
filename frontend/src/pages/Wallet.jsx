import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useStore } from '../store/useStore'
import Toast from '../components/Toast'

const TX_LABEL = {
  deposit: 'Пополнение',
  withdraw: 'Вывод',
  bet: 'Ставка',
  win: 'Выигрыш',
  bonus: 'Бонус',
}

export default function Wallet() {
  const navigate = useNavigate()
  const { balance, deposit, refreshBalance } = useStore()
  const [txs, setTxs] = useState([])
  const [busy, setBusy] = useState(false)
  const [toast, setToast] = useState('')

  const load = () => api.transactions().then(setTxs).catch(() => {})

  useEffect(() => {
    refreshBalance()
    load()
  }, [refreshBalance])

  const topUp = async (amount) => {
    setBusy(true)
    try {
      await deposit(amount)
      await load()
      setToast(`+${amount} ★ зачислено`)
    } catch (e) {
      setToast(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <div className="page-top">
        <button className="back-btn" onClick={() => navigate('/')}>
          ‹
        </button>
        <div className="page-title">💰 Кошелёк</div>
      </div>

      <div className="banner" style={{ minHeight: 80, marginBottom: 18 }}>
        <p style={{ opacity: 0.8 }}>Баланс</p>
        <h1 style={{ fontSize: 40 }}>
          {balance.toLocaleString('ru-RU', { maximumFractionDigits: 2 })} ★
        </h1>
      </div>

      <div className="label">Пополнить (демо)</div>
      <div className="chip-row" style={{ marginBottom: 20 }}>
        {[100, 500, 1000, 5000].map((a) => (
          <button
            key={a}
            className="chip"
            disabled={busy}
            onClick={() => topUp(a)}
          >
            +{a} ★
          </button>
        ))}
      </div>

      <div className="label">История операций</div>
      <div className="panel" style={{ marginTop: 8 }}>
        {txs.length === 0 && (
          <div className="muted center" style={{ padding: 12 }}>
            Пока нет операций
          </div>
        )}
        {txs.map((t) => (
          <div
            key={t.id}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: '10px 0',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div>
              <div style={{ fontWeight: 700 }}>{TX_LABEL[t.type] || t.type}</div>
              <div className="muted" style={{ fontSize: 11 }}>
                {t.game || '—'}
              </div>
            </div>
            <div
              style={{
                fontWeight: 800,
                color: t.amount >= 0 ? 'var(--green)' : 'var(--danger)',
              }}
            >
              {t.amount >= 0 ? '+' : ''}
              {Number(t.amount).toFixed(2)} ★
            </div>
          </div>
        ))}
      </div>

      <Toast message={toast} onClose={() => setToast('')} />
    </div>
  )
}
