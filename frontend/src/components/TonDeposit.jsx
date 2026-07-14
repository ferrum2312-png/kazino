import { useEffect, useState } from 'react'
import { useTonConnectUI, useTonAddress } from '@tonconnect/ui-react'
import { depositTon } from '../ton'
import { useI18n } from '../i18n'
import { useStore } from '../store/useStore'
import { api } from '../api/client'

const AMOUNTS = [0.5, 1, 5, 10]

export default function TonDeposit({ onDone }) {
  const { t } = useI18n()
  const { user } = useStore()
  const [tonConnectUI] = useTonConnectUI()
  const address = useTonAddress()
  const [amount, setAmount] = useState(1)
  const [rate, setRate] = useState(null) // stars per GRAM
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    api
      .getRate()
      .then((r) => setRate(r.stars_per_coin))
      .catch(() => {})
  }, [])

  const estStars = rate ? Math.floor(amount * rate) : null

  const submit = async () => {
    if (!address) {
      tonConnectUI.openModal()
      return
    }
    if (!user?.id) {
      setMsg(t('depositCancelled'))
      return
    }
    setBusy(true)
    setMsg('')
    try {
      await depositTon(tonConnectUI, amount, `dep:${user.id}`)
      setMsg(t('depositSent', { n: amount }))
      onDone?.(amount)
    } catch {
      setMsg(t('depositCancelled'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="label">{t('amount')} (GRAM)</div>
      <div className="chip-row">
        {AMOUNTS.map((a) => (
          <button
            key={a}
            className={`chip ${amount === a ? 'active' : ''}`}
            onClick={() => setAmount(a)}
          >
            {a}
          </button>
        ))}
      </div>

      {rate && (
        <div className="muted" style={{ marginTop: 10, fontSize: 13 }}>
          {t('perCoin', { n: Math.floor(rate) })} · {t('youGet', { n: estStars })}
        </div>
      )}

      <button
        className="btn blue block"
        style={{ marginTop: 14 }}
        disabled={busy}
        onClick={submit}
      >
        {address ? t('depositTonBtn', { n: amount }) : t('connectWallet')}
      </button>
      {msg && (
        <div className="center" style={{ marginTop: 10, fontWeight: 700 }}>
          {msg}
        </div>
      )}
    </div>
  )
}
