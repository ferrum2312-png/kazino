const API_BASE = import.meta.env.VITE_API_BASE || '/api'

let authToken = localStorage.getItem('token') || null

export function setToken(token) {
  authToken = token
  if (token) localStorage.setItem('token', token)
  else localStorage.removeItem('token')
}

export function getToken() {
  return authToken
}

async function request(path, { method = 'GET', body, form } = {}) {
  const headers = {}
  let payload

  if (form) {
    payload = new URLSearchParams(form)
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
  } else if (body !== undefined) {
    payload = JSON.stringify(body)
    headers['Content-Type'] = 'application/json'
  }

  if (authToken) headers['Authorization'] = `Bearer ${authToken}`

  const res = await fetch(`${API_BASE}${path}`, { method, headers, body: payload })

  if (res.status === 204) return null
  const data = await res.json().catch(() => null)

  if (!res.ok) {
    const detail = data?.detail
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join(', ')
      : detail || `Request failed (${res.status})`
    throw new Error(message)
  }
  return data
}

export const api = {
  telegramAuth: (init_data) =>
    request('/auth/telegram', { method: 'POST', body: { init_data } }),
  register: (username, password, email) =>
    request('/auth/register', { method: 'POST', body: { username, password, email } }),
  login: (username, password) =>
    request('/auth/login', { method: 'POST', form: { username, password } }),
  me: () => request('/users/me'),
  balance: () => request('/users/me/balance'),
  deposit: (amount) =>
    request('/users/me/deposit', { method: 'POST', body: { amount } }),
  transactions: () => request('/users/me/transactions'),

  games: () => request('/catalog/games'),
  banner: () => request('/catalog/banner'),

  // Mines
  minesStart: (bet, mines) =>
    request('/games/mines/start', { method: 'POST', body: { bet, mines } }),
  minesReveal: (game_id, tile) =>
    request('/games/mines/reveal', { method: 'POST', body: { game_id, tile } }),
  minesCashout: (game_id) =>
    request('/games/mines/cashout', { method: 'POST', body: { game_id } }),
  minesActive: () => request('/games/mines/active'),

  // Crash
  crashHistory: () => request('/games/crash/history'),
}

export function crashSocketUrl() {
  const base = import.meta.env.VITE_WS_BASE
  if (base) return `${base}/games/crash/ws`
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${location.host}/api/games/crash/ws`
}
