import { useState } from 'react'
import { useTonConnectUI, useTonAddress } from '@tonconnect/ui-react'
import { useStore } from '../store/useStore'
import { useI18n } from '../i18n'
import Toast from '../components/Toast'
import Settings from '../components/Settings'
import DepositSheet from '../components/DepositSheet'

function shortAddr(a) {
  return a ? `${a.slice(0, 4)}…${a.slice(-4)}` : ''
}

export default function Profile() {
  const { user, balance } = useStore()
  const { t } = useI18n()
  const [tonConnectUI] = useTonConnectUI()
  const address = useTonAddress()
  const [toast, setToast] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [showDeposit, setShowDeposit] = useState(false)

  const connect = () => tonConnectUI.openModal()
  const disconnect = () => tonConnectUI.disconnect()

  const name = user?.username || user?.first_name || `Игрок ${user?.id ?? ''}`
  const handle = user?.username ? `@${user.username}` : `id${user?.id ?? ''}`
  const avatar =
    user?.avatar_url || 'https://api.dicebear.com/7.x/thumbs/svg?seed=guest'

  return (
    <div className="app profile">
      {/* top bar */}
      <div className="pf-top">
        <div className="pf-top-left">
          <button className="pf-icon-btn" onClick={() => setShowSettings(true)}>
            ⚙️
          </button>
          <div className="pf-online">
            <span className="pf-people">👤</span> 54
          </div>
        </div>
        <button className="pf-ton-pill">
          <span className="pf-diamond" onClick={address ? disconnect : connect}>
            💎
          </span>
          <span onClick={address ? disconnect : connect}>
            {address ? shortAddr(address) : '0.00'}
          </span>
          <span className="pf-plus" onClick={() => setShowDeposit(true)}>
            +
          </span>
        </button>
      </div>

      {/* profile card (no level bar) */}
      <div className="pf-card pf-profile">
        <img className="pf-avatar" src={avatar} alt="" />
        <div className="pf-info">
          <div className="pf-name">{name}</div>
          <div className="pf-handle">{handle}</div>
        </div>
      </div>

      {/* TON balance / connect */}
      <button
        className="pf-card pf-balance"
        onClick={address ? () => setShowDeposit(true) : connect}
      >
        <span className="pf-coin ton">💎</span>
        <div className="pf-bal-info">
          <div className="pf-bal-label">{t('balanceTon')}</div>
          <div className="pf-bal-value">
            {address ? '0.00' : `${t('connectWallet')} →`}
          </div>
        </div>
        {address && <span className="pf-chip">{shortAddr(address)}</span>}
      </button>

      {/* game coin balance */}
      <div className="pf-card pf-balance">
        <span className="pf-coin star">★</span>
        <div className="pf-bal-info">
          <div className="pf-bal-label">{t('balance')}</div>
          <div className="pf-bal-value">{balance.toLocaleString('ru-RU')} ★</div>
        </div>
        <button className="pf-help" onClick={() => setToast(t('coinsHint'))}>
          ?
        </button>
      </div>

      {/* actions */}
      <div className="pf-actions">
        <button className="btn blue" onClick={() => setShowDeposit(true)}>
          {t('topUp')}
        </button>
        <button className="btn dark" onClick={() => setToast(t('supportHint'))}>
          {t('support')}
        </button>
      </div>

      {/* empty state */}
      <div className="pf-card pf-empty">
        <div className="pf-duck">🦆</div>
        <div className="pf-empty-title">{t('giftsTitle')}</div>
        <div className="pf-empty-sub">{t('giftsSub')}</div>
        <button className="btn dark pf-how" onClick={() => setToast(t('soon'))}>
          {t('howAdd')}
        </button>
      </div>

      {showSettings && <Settings onClose={() => setShowSettings(false)} />}
      {showDeposit && <DepositSheet onClose={() => setShowDeposit(false)} />}

      <Toast message={toast} onClose={() => setToast('')} />
    </div>
  )
}
