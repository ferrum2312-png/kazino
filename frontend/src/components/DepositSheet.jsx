import { useState } from 'react'
import { useI18n } from '../i18n'
import TonDeposit from './TonDeposit'
import StarsDeposit from './StarsDeposit'
import CryptoDeposit from './CryptoDeposit'
import Toast from './Toast'

const METHODS = [
  { key: 'gifts', icon: '🎁', ready: false },
  { key: 'ton', icon: '💎', min: '0.1', ready: true },
  { key: 'stars', icon: '✈️', min: '1', ready: true },
  { key: 'cryptobot', icon: '🪙', min: '0.1', ready: true },
]

const TITLES = { ton: 'Toncoin', stars: 'Telegram Stars', cryptobot: 'Crypto Bot' }

export default function DepositSheet({ onClose }) {
  const { t } = useI18n()
  const [selected, setSelected] = useState('ton')
  const [step, setStep] = useState('methods') // methods | amount
  const [toast, setToast] = useState('')

  const method = METHODS.find((m) => m.key === selected)

  const cont = () => {
    if (!method?.ready) {
      setToast(t('soon'))
      return
    }
    setStep('amount')
  }

  const renderStep = () => {
    if (selected === 'ton') return <TonDeposit onDone={onClose} />
    if (selected === 'stars') return <StarsDeposit onDone={onClose} />
    if (selected === 'cryptobot') return <CryptoDeposit onDone={onClose} />
    return null
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-sheet" onClick={(e) => e.stopPropagation()}>
        {step === 'methods' ? (
          <>
            <div className="modal-title center">{t('topUpTitle')}</div>

            <div className="dep-methods">
              {METHODS.map((m) => (
                <button
                  key={m.key}
                  className={`dep-method ${selected === m.key ? 'active' : ''}`}
                  onClick={() => setSelected(m.key)}
                >
                  <span className="dep-ic">{m.icon}</span>
                  <div className="dep-info">
                    <div className="dep-name">{t(`m_${m.key}`)}</div>
                    <div className="dep-sub">
                      {m.ready ? t(`m_${m.key}_sub`) : t('soon')}
                    </div>
                  </div>
                  {m.min && (
                    <span className="dep-min">
                      {t('from')} {m.min}
                    </span>
                  )}
                </button>
              ))}
            </div>

            <button
              className="btn blue block"
              style={{ marginTop: 14 }}
              onClick={cont}
            >
              {t('continue')}
            </button>
          </>
        ) : (
          <>
            <div className="modal-title">{TITLES[selected]}</div>
            {renderStep()}
            <button
              className="btn ghost block"
              style={{ marginTop: 10 }}
              onClick={() => setStep('methods')}
            >
              ‹ {t('back')}
            </button>
          </>
        )}

        <Toast message={toast} onClose={() => setToast('')} />
      </div>
    </div>
  )
}
