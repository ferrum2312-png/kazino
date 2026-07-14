import { create } from 'zustand'
import { api, setToken, getToken } from '../api/client'

function telegramInitData() {
  return window.Telegram?.WebApp?.initData || ''
}

export const useStore = create((set, get) => ({
  user: null,
  balance: 0,
  loading: true,
  inTelegram: !!window.Telegram?.WebApp?.initData,

  async bootstrap() {
    // Inside Telegram: authenticate ONLY from the fresh, signed initData so the
    // session is bound to the current Telegram user. Never fall back to a token
    // already in localStorage — it may belong to a different account.
    const initData = telegramInitData()
    if (initData) {
      try {
        await get().loginWithTelegram(initData)
      } catch {
        setToken(null)
        set({ user: null })
      }
      set({ loading: false })
      return
    }

    if (!getToken()) {
      set({ loading: false })
      return
    }
    try {
      const user = await api.me()
      set({ user, balance: Number(user.balance), loading: false })
    } catch {
      setToken(null)
      set({ user: null, loading: false })
    }
  },

  async loginWithTelegram(initData) {
    const { access_token } = await api.telegramAuth(
      initData || telegramInitData()
    )
    setToken(access_token)
    const user = await api.me()
    set({ user, balance: Number(user.balance) })
  },

  async login(username, password) {
    const { access_token } = await api.login(username, password)
    setToken(access_token)
    const user = await api.me()
    set({ user, balance: Number(user.balance) })
  },

  async register(username, password, email) {
    const { access_token } = await api.register(username, password, email || null)
    setToken(access_token)
    const user = await api.me()
    set({ user, balance: Number(user.balance) })
  },

  logout() {
    setToken(null)
    set({ user: null, balance: 0 })
  },

  setBalance(balance) {
    set({ balance: Number(balance) })
  },

  async refreshBalance() {
    try {
      const { balance } = await api.balance()
      set({ balance: Number(balance) })
    } catch {
      /* ignore */
    }
  },

  async deposit(amount) {
    const { balance } = await api.deposit(amount)
    set({ balance: Number(balance) })
  },
}))
