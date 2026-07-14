import { useState } from 'react'
import { useTonConnectUI, useTonAddress } from '@tonconnect/ui-react'
import { depositTon } from '../ton'
import { useI18n } from '../i18n'

const AMOUNTS = [0.5, 1, 5, 10]

export default function TonDeposit({ onDone }) {
  const { t } = useI18n()
  const [tonConnectUI] = useTonConnectUI()
  const address = useTonAddress()
  const [amount, setAmount] = useState(1)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  const submit = async () => {
    if (!address) {
      tonConnectUI.openModal()
      return
    }
    setBusy(true)
    setMsg('')
    try {
      await depositTon(tonConnectUI, amount)
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
      <div className="label">{t('amount')} (TON)</div>
      <div className="chip-row">
        {AMOUNTS.map((a) => (
          <button
            key={a}
            className={`chip ${amount === a ? 'active' : ''}`}
            onClick={() => setAmount(a)}
          >
            {a} TON
          </button>
        ))}
      </div>
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
