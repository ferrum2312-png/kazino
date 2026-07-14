import Header from '../components/Header'
import { useI18n } from '../i18n'

export default function Cases() {
  const { t } = useI18n()
  return (
    <div className="app">
      <Header />
      <div className="panel center" style={{ padding: 44, marginTop: 20 }}>
        <div style={{ fontSize: 64, marginBottom: 14 }}>🎁</div>
        <div style={{ fontSize: 22, fontWeight: 900 }}>{t('casesTitle')}</div>
        <p className="muted" style={{ marginTop: 8 }}>
          {t('casesSub')}
        </p>
      </div>
    </div>
  )
}
