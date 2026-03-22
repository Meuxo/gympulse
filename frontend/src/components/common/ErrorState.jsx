export default function ErrorState({ message = 'Something went wrong', onRetry }) {
  return (
    <div className="error-state">
      <p>{message}</p>
      {onRetry && (
        <button className="btn btn-danger btn-sm mt-md" onClick={onRetry}>
          Try Again
        </button>
      )}
    </div>
  )
}
