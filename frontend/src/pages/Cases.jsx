import Header from '../components/Header'

export default function Cases() {
  return (
    <div className="app">
      <Header />
      <div className="panel center" style={{ padding: 44, marginTop: 20 }}>
        <div style={{ fontSize: 64, marginBottom: 14 }}>🎁</div>
        <div style={{ fontSize: 22, fontWeight: 900 }}>Кейсы</div>
        <p className="muted" style={{ marginTop: 8 }}>
          Скоро — открывай кейсы и забирай призы
        </p>
      </div>
    </div>
  )
}
