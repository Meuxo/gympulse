export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="loading-page">
      <div>
        <div className="spinner" />
        <p className="text-muted" style={{ textAlign: 'center', marginTop: 12 }}>{message}</p>
      </div>
    </div>
  )
}
