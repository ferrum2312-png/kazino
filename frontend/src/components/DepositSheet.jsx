import { useState } from 'react'
import { useTonConnectUI, useTonAddress } from '@tonconnect/ui-react'
import { useI18n } from '../i18n'
import TonDeposit from './TonDeposit'
import Toast from './Toast'

const METHODS = [
  { key: 'gifts', icon: '🎁', ready: false },
  { key: 'ton', icon: '💎', min: '0.1', ready: true },
  { key: 'stars', icon: '✈️', min: '1', ready: false },
  { key: 'cryptobot', icon: '🪙', min: '0.1', ready: false },
]

export default function DepositSheet({ onClose }) {
  const { t } = useI18n()
  const [tonConnectUI] = useTonConnectUI()
  const address = useTonAddress()
  const [selected, setSelected] = useState('ton')
  const [step, setStep] = useState('methods') // methods | amount
  const [toast, setToast] = useState('')

  const method = METHODS.find((m) => m.key === selected)

  const cont = () => {
    if (!method?.ready) {
      setToast(t('soon'))
      return
    }
    if (selected === 'ton') setStep('amount')
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
              className="btn dark block"
              style={{ marginTop: 14 }}
              onClick={() => !address && tonConnectUI.openModal()}
            >
              {address ? t('walletLinked') : t('linkWallet')}
            </button>

            <button
              className="btn blue block dep-continue"
              style={{ marginTop: 10 }}
              onClick={cont}
            >
              <span>{t('continue')}</span>
              {selected === 'ton' && (
                <span className="dep-continue-sub">
                  {t('minAmount', { n: '0.1' })}
                </span>
              )}
            </button>
          </>
        ) : (
          <>
            <div className="modal-title">Toncoin</div>
            <TonDeposit onDone={onClose} />
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
