import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../store/useStore'
import { useI18n } from '../i18n'
import DepositSheet from '../components/DepositSheet'

export default function Wallet() {
  const navigate = useNavigate()
  const { balance, refreshBalance } = useStore()
  const { t } = useI18n()
  const [showDeposit, setShowDeposit] = useState(false)

  useEffect(() => {
    refreshBalance()
  }, [refreshBalance])

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

      <button className="btn blue block" onClick={() => setShowDeposit(true)}>
        {t('topUp')}
      </button>

      {showDeposit && <DepositSheet onClose={() => setShowDeposit(false)} />}
    </div>
  )
}
