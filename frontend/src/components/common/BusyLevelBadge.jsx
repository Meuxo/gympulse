const COLORS = {
  1: { bg: 'var(--green-soft)', color: 'var(--green)' },
  2: { bg: 'rgba(110,231,183,.12)', color: '#6ee7b7' },
  3: { bg: 'var(--yellow-soft)', color: 'var(--yellow)' },
  4: { bg: 'rgba(251,146,60,.12)', color: '#fb923c' },
  5: { bg: 'var(--red-soft)', color: 'var(--red)' },
}
const LABELS = { 1: 'Empty', 2: 'Light', 3: 'Moderate', 4: 'Busy', 5: 'Packed' }

export default function BusyLevelBadge({ level, label }) {
  const rounded = Math.round(level || 0)
  const style = COLORS[rounded] || COLORS[3]
  return (
    <span className="badge" style={{ background: style.bg, color: style.color }}>
      {label || LABELS[rounded] || 'Unknown'}
    </span>
  )
}
