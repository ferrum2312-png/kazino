import { useEffect, useState } from 'react'
import Header from '../components/Header'
import GameCard from '../components/GameCard'
import { api } from '../api/client'
import { useStore } from '../store/useStore'

export default function Home() {
  const [games, setGames] = useState([])
  const [loading, setLoading] = useState(true)
  const { refreshBalance } = useStore()

  useEffect(() => {
    refreshBalance()
    api
      .games()
      .then((g) => setGames(g.games))
      .finally(() => setLoading(false))
  }, [refreshBalance])

  return (
    <div className="app">
      <Header />

      {loading ? (
        <div className="spinner" />
      ) : (
        <div className="card-list">
          {games.map((g) => (
            <GameCard key={g.slug} game={g} />
          ))}
        </div>
      )}
    </div>
  )
}
