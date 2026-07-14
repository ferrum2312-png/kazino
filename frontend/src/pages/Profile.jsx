import { useState } from 'react'
import { useTonConnectUI, useTonAddress } from '@tonconnect/ui-react'
import { useStore } from '../store/useStore'
import Toast from '../components/Toast'

function shortAddr(a) {
  return a ? `${a.slice(0, 4)}…${a.slice(-4)}` : ''
}

export default function Profile() {
  const { user, balance } = useStore()
  const [tonConnectUI] = useTonConnectUI()
  const address = useTonAddress()
  const [toast, setToast] = useState('')

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
          <button
            className="pf-icon-btn"
            onClick={() => setToast('Настройки скоро')}
          >
            ⚙️
          </button>
          <div className="pf-online">
            <span className="pf-people">👤</span> 54
          </div>
        </div>
        <button
          className="pf-ton-pill"
          onClick={address ? disconnect : connect}
        >
          <span className="pf-diamond">💎</span>
          <span>{address ? shortAddr(address) : '0.00'}</span>
          <span className="pf-plus">+</span>
        </button>
      </div>

      {/* profile card */}
      <div className="pf-card pf-profile">
        <img className="pf-avatar" src={avatar} alt="" />
        <div className="pf-info">
          <div className="pf-name">{name}</div>
          <div className="pf-handle">{handle}</div>
          <div className="pf-level-bar">
            <div className="pf-level-fill" style={{ width: '4%' }}>
              <span className="pf-level-a">0 → 1 Ур.</span>
              <span className="pf-level-b">0/0</span>
            </div>
          </div>
        </div>
      </div>

      {/* TON balance / connect */}
      <button
        className="pf-card pf-balance"
        onClick={address ? disconnect : connect}
      >
        <span className="pf-coin ton">💎</span>
        <div className="pf-bal-info">
          <div className="pf-bal-label">Баланс TON</div>
          <div className="pf-bal-value">
            {address ? '0.00' : 'Подключить кошелёк →'}
          </div>
        </div>
        {address && <span className="pf-chip">{shortAddr(address)}</span>}
      </button>

      {/* game coin balance */}
      <div className="pf-card pf-balance">
        <span className="pf-coin star">★</span>
        <div className="pf-bal-info">
          <div className="pf-bal-label">Баланс</div>
          <div className="pf-bal-value">
            {balance.toLocaleString('ru-RU')} ★
          </div>
        </div>
        <button
          className="pf-help"
          onClick={() => setToast('Игровые фишки. Начисляются новым игрокам.')}
        >
          ?
        </button>
      </div>

      {/* actions */}
      <div className="pf-actions">
        <button className="btn blue" onClick={() => setToast('Скоро')}>
          Добавить подарок
        </button>
        <button
          className="btn dark"
          onClick={() => setToast('Напиши в поддержку через бота')}
        >
          Тех. поддержка
        </button>
      </div>

      {/* empty state */}
      <div className="pf-card pf-empty">
        <div className="pf-duck">🦆</div>
        <div className="pf-empty-title">Есть подарки в Telegram?</div>
        <div className="pf-empty-sub">Добавь их через нашего бота</div>
        <button className="btn dark pf-how" onClick={() => setToast('Скоро')}>
          Как добавить?
        </button>
      </div>

      <Toast message={toast} onClose={() => setToast('')} />
    </div>
  )
}
