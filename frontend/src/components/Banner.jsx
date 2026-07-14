export default function Banner({ title, subtitle }) {
  return (
    <div className="banner">
      <span className="glow-777">777</span>
      <h1>{title || 'Выбей 777'}</h1>
      <p>{subtitle || 'и получи NFT подарок'}</p>
    </div>
  )
}
