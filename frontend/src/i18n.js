import { create } from 'zustand'

const dict = {
  ru: {
    // nav
    home: 'Главная',
    cases: 'Кейсы',
    profile: 'Профиль',
    crash: 'Краш',
    mines: 'Мины',
    wallet: 'Кошелёк',
    // profile
    balanceTon: 'Баланс TON',
    balance: 'Баланс',
    connectWallet: 'Подключить кошелёк',
    addGift: 'Добавить подарок',
    support: 'Тех. поддержка',
    coinsHint: 'Игровые фишки. Начисляются новым игрокам.',
    giftsTitle: 'Есть подарки в Telegram?',
    giftsSub: 'Добавь их через нашего бота',
    howAdd: 'Как добавить?',
    soon: 'Скоро',
    supportHint: 'Напиши в поддержку через бота',
    // settings
    settings: 'Настройки',
    language: 'Язык',
    close: 'Закрыть',
    // wallet / deposit
    topUp: 'Пополнить',
    tonTopUp: 'Пополнение через TON',
    amount: 'Сумма',
    depositTonBtn: 'Пополнить {n} GRAM',
    connectFirst: 'Сначала подключи кошелёк',
    depositSent: 'Платёж на {n} GRAM отправлен',
    depositCancelled: 'Платёж отменён',
    youGet: 'Получишь ≈ {n} ★',
    perCoin: '1 GRAM ≈ {n} ★',
    balanceLabel: 'Баланс',
    demoTopUp: 'Демо‑пополнение',
    // cases
    casesTitle: 'Кейсы',
    casesSub: 'Скоро — открывай кейсы и забирай призы',
    // games subtitles
    sub_crash: 'Успей забрать до взрыва',
    sub_mines: 'Обходи бомбы',
    sub_duel: '1 на 1',
    sub_arena: 'Сражайся за джекпот',
  },
  en: {
    home: 'Home',
    cases: 'Cases',
    profile: 'Profile',
    crash: 'Crash',
    mines: 'Mines',
    wallet: 'Wallet',
    balanceTon: 'TON Balance',
    balance: 'Balance',
    connectWallet: 'Connect wallet',
    addGift: 'Add gift',
    support: 'Support',
    coinsHint: 'In-game chips. Credited to new players.',
    giftsTitle: 'Got gifts in Telegram?',
    giftsSub: 'Add them via our bot',
    howAdd: 'How to add?',
    soon: 'Soon',
    supportHint: 'Message support via the bot',
    settings: 'Settings',
    language: 'Language',
    close: 'Close',
    topUp: 'Top up',
    tonTopUp: 'Top up with TON',
    amount: 'Amount',
    depositTonBtn: 'Deposit {n} GRAM',
    connectFirst: 'Connect a wallet first',
    depositSent: 'Payment of {n} GRAM sent',
    depositCancelled: 'Payment cancelled',
    youGet: "You'll get ≈ {n} ★",
    perCoin: '1 GRAM ≈ {n} ★',
    balanceLabel: 'Balance',
    demoTopUp: 'Demo top-up',
    casesTitle: 'Cases',
    casesSub: 'Coming soon — open cases and grab prizes',
    sub_crash: 'Cash out before it crashes',
    sub_mines: 'Avoid the bombs',
    sub_duel: '1 vs 1',
    sub_arena: 'Fight for the jackpot',
  },
}

// Game card titles per language (backend titles are Russian by default).
export const gameTitles = {
  'ralph-arena': { ru: 'VAVADA АРЕНА', en: 'VAVADA ARENA' },
  duel: { ru: 'ПВП ДУЭЛЬ', en: 'PVP DUEL' },
  crash: { ru: 'КРАШ', en: 'CRASH' },
  mines: { ru: 'МИНЫ', en: 'MINES' },
}

export const useI18n = create((set, get) => ({
  lang: localStorage.getItem('lang') || 'ru',
  setLang(lang) {
    localStorage.setItem('lang', lang)
    set({ lang })
  },
  t(key, vars) {
    const l = get().lang
    let s = (dict[l] && dict[l][key]) ?? dict.ru[key] ?? key
    if (vars) {
      for (const [k, v] of Object.entries(vars)) {
        s = s.replace(`{${k}}`, v)
      }
    }
    return s
  },
}))
