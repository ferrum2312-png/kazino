import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../store/useStore'
import { useI18n } from '../i18n'
import TonDeposit from '../components/TonDeposit'
import Toast from '../components/Toast'

export default function Wallet() {
  const navigate = useNavigate()
  const { balance, deposit, refreshBalance } = useStore()
  const { t } = useI18n()
  const [busy, setBusy] = useState(false)
  const [toast, setToast] = useState('')

  useEffect(() => {
    refreshBalance()
  }, [refreshBalance])

  const demoTopUp = async (amount) => {
    setBusy(true)
    try {
      await deposit(amount)
      setToast(`+${amount} ★`)
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
        <div className="page-title">💰 {t('wallet')}</div>
      </div>

      <div className="banner" style={{ minHeight: 80, marginBottom: 18 }}>
        <p style={{ opacity: 0.8 }}>{t('balanceLabel')}</p>
        <h1 style={{ fontSize: 40 }}>
          {balance.toLocaleString('ru-RU', { maximumFractionDigits: 2 })} ★
        </h1>
      </div>

      {/* TON top-up */}
      <div className="label">{t('tonTopUp')}</div>
      <div className="panel" style={{ marginTop: 8, marginBottom: 20 }}>
        <TonDeposit onDone={() => refreshBalance()} />
      </div>

      {/* demo top-up (play money) */}
      <div className="label">{t('demoTopUp')}</div>
      <div className="chip-row">
        {[100, 500, 1000, 5000].map((a) => (
          <button
            key={a}
            className="chip"
            disabled={busy}
            onClick={() => demoTopUp(a)}
          >
            +{a} ★
          </button>
        ))}
      </div>

      <Toast message={toast} onClose={() => setToast('')} />
    </div>
  )
}
