import { useState } from 'react'
import { api } from '../api/client'
import { useI18n } from '../i18n'
import { useStore } from '../store/useStore'

const AMOUNTS = {
  TON: [0.1, 0.5, 1, 5, 10],
  USDT: [1, 5, 10, 50, 100],
}

export default function CryptoDeposit({ onDone }) {
  const { t } = useI18n()
  const { refreshBalance } = useStore()
  const [asset, setAsset] = useState('TON')
  const [amount, setAmount] = useState(1)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  const amounts = AMOUNTS[asset]

  const pickAsset = (a) => {
    setAsset(a)
    setAmount(AMOUNTS[a][2])
  }

  const pay = async () => {
    setBusy(true)
    setMsg('')
    try {
      const { pay_url } = await api.cryptobotInvoice(amount, asset)
      const tg = window.Telegram?.WebApp
      if (pay_url && tg?.openTelegramLink && pay_url.includes('t.me')) {
        tg.openTelegramLink(pay_url)
      } else if (pay_url && tg?.openLink) {
        tg.openLink(pay_url)
      } else if (pay_url) {
        window.open(pay_url, '_blank')
      }
      setMsg(t('payOpened'))
      let n = 0
      const iv = setInterval(() => {
        refreshBalance()
        if (++n >= 10) clearInterval(iv)
      }, 2000)
      onDone?.()
    } catch (e) {
      setMsg(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="chip-row" style={{ marginBottom: 12 }}>
        {['TON', 'USDT'].map((a) => (
          <button
            key={a}
            className={`chip ${asset === a ? 'active' : ''}`}
            onClick={() => pickAsset(a)}
          >
            {a}
          </button>
        ))}
      </div>
      <div className="label">
        {t('amount')} ({asset})
      </div>
      <div className="chip-row">
        {amounts.map((a) => (
          <button
            key={a}
            className={`chip ${amount === a ? 'active' : ''}`}
            onClick={() => setAmount(a)}
          >
            {a}
          </button>
        ))}
      </div>
      <button
        className="btn blue block"
        style={{ marginTop: 14 }}
        disabled={busy}
        onClick={pay}
      >
        {t('payCrypto', { n: amount, a: asset })}
      </button>
      {msg && (
        <div className="center" style={{ marginTop: 10, fontWeight: 700 }}>
          {msg}
        </div>
      )}
    </div>
  )
}
