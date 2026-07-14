import { useI18n } from '../i18n'

export default function Settings({ onClose }) {
  const { t, lang, setLang } = useI18n()

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-sheet" onClick={(e) => e.stopPropagation()}>
        <div className="modal-title">{t('settings')}</div>

        <div className="modal-row-label">{t('language')}</div>
        <div className="lang-switch">
          <button
            className={`lang-btn ${lang === 'ru' ? 'active' : ''}`}
            onClick={() => setLang('ru')}
          >
            🇷🇺 Русский
          </button>
          <button
            className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
            onClick={() => setLang('en')}
          >
            🇬🇧 English
          </button>
        </div>

        <button className="btn dark block" style={{ marginTop: 18 }} onClick={onClose}>
          {t('close')}
        </button>
      </div>
    </div>
  )
}
