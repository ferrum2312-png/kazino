import { useState } from 'react'
import { api } from '../api/client'
import { useI18n } from '../i18n'
import { useStore } from '../store/useStore'

const AMOUNTS = [25, 50, 100, 250, 500, 1000, 2500, 5000]

export default function StarsDeposit({ onDone }) {
  const { t } = useI18n()
  const { refreshBalance } = useStore()
  const [amount, setAmount] = useState(50)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  const pollBalance = () => {
    let n = 0
    const iv = setInterval(() => {
      refreshBalance()
      if (++n >= 6) clearInterval(iv)
    }, 1500)
  }

  const pay = async () => {
    setBusy(true)
    setMsg('')
    try {
      const { link } = await api.starsInvoice(amount)
      const tg = window.Telegram?.WebApp
      if (tg?.openInvoice) {
        tg.openInvoice(link, (status) => {
          setBusy(false)
          if (status === 'paid') {
            setMsg(t('paid'))
            pollBalance()
            onDone?.()
          } else if (status === 'cancelled') {
            setMsg(t('depositCancelled'))
          } else {
            setMsg(t('payFailed'))
          }
        })
      } else {
        window.open(link, '_blank')
        setBusy(false)
      }
    } catch (e) {
      setMsg(e.message)
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="label">{t('amount')} (★)</div>
      <div className="chip-row">
        {AMOUNTS.map((a) => (
          <button
            key={a}
            className={`chip ${amount === a ? 'active' : ''}`}
            onClick={() => setAmount(a)}
          >
            {a} ★
          </button>
        ))}
      </div>
      <button
        className="btn blue block"
        style={{ marginTop: 14 }}
        disabled={busy}
        onClick={pay}
      >
        {t('payStars', { n: amount })}
      </button>
      {msg && (
        <div className="center" style={{ marginTop: 10, fontWeight: 700 }}>
          {msg}
        </div>
      )}
    </div>
  )
}
