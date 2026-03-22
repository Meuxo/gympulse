import { useState, useEffect } from 'react'
import { gymAPI } from '../../services/api'

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const BAR_COLORS = ['var(--green)', 'var(--green)', 'var(--yellow)', 'var(--accent)', 'var(--red)']

function getBarColor(level) {
  if (level <= 1) return 'var(--green)'
  if (level <= 2) return '#6ee7b7'
  if (level <= 3) return 'var(--yellow)'
  if (level <= 4) return 'var(--accent)'
  return 'var(--red)'
}

export default function PopularTimes({ gymId }) {
  const [data, setData] = useState(null)
  const [selectedDay, setSelectedDay] = useState(new Date().getDay() === 0 ? 6 : new Date().getDay() - 1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!gymId) return
    setLoading(true)
    gymAPI.getPopularTimes(gymId)
      .then((res) => {
        setData(res.data)
        // Set to current day
        const today = new Date().getDay()
        setSelectedDay(today === 0 ? 6 : today - 1)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [gymId])

  if (loading || !data) return null

  const dayData = data.days?.[selectedDay]
  if (!dayData) return null

  // Only show hours 5am - 11pm
  const hours = dayData.hours.filter((h) => h.hour >= 5 && h.hour <= 23)
  const maxLevel = Math.max(...hours.map((h) => h.level), 1)

  return (
    <div className="card">
      <div className="card-title">Popular Times</div>

      {/* Day selector */}
      <div className="flex gap-xs mb-md" style={{ overflowX: 'auto' }}>
        {DAYS.map((d, i) => (
          <button
            key={i}
            className={`btn btn-sm ${selectedDay === i ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setSelectedDay(i)}
            style={{ minWidth: 44, padding: '5px 8px', fontSize: '0.72rem' }}
          >
            {d}
          </button>
        ))}
      </div>

      {/* Bar chart */}
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 100 }}>
        {hours.map((h) => {
          const height = maxLevel > 0 ? (h.level / 5) * 100 : 0
          const isCurrent = data.current_hour === h.hour && selectedDay === (new Date().getDay() === 0 ? 6 : new Date().getDay() - 1)
          return (
            <div
              key={h.hour}
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                height: '100%',
                justifyContent: 'flex-end',
              }}
              title={`${h.hour}:00 — ${h.level.toFixed(1)}/5`}
            >
              <div
                style={{
                  width: '100%',
                  height: `${Math.max(height, 2)}%`,
                  background: isCurrent ? 'var(--primary)' : getBarColor(h.level),
                  borderRadius: '3px 3px 0 0',
                  opacity: h.level < 0.3 ? 0.2 : isCurrent ? 1 : 0.65,
                  transition: 'height .2s',
                }}
              />
            </div>
          )
        })}
      </div>

      {/* Hour labels */}
      <div style={{ display: 'flex', gap: 2, marginTop: 4 }}>
        {hours.map((h) => (
          <div
            key={h.hour}
            style={{
              flex: 1,
              textAlign: 'center',
              fontSize: '0.55rem',
              color: 'var(--text-3)',
            }}
          >
            {h.hour % 3 === 0 ? (h.hour > 12 ? `${h.hour - 12}p` : h.hour === 0 ? '12a' : `${h.hour}a`) : ''}
          </div>
        ))}
      </div>

      {data.current_hour_level != null && (
        <div className="text-xs text-2 mt-sm">
          Right now: <span className="font-semibold text-0">{data.current_hour_level.toFixed(1)}/5</span> busyness
        </div>
      )}

      {data.data_source === 'google_estimated' && (
        <div className="text-xs mt-xs" style={{ color: 'var(--accent)', opacity: 0.8 }}>
          Based on typical gym patterns &middot; Google data
        </div>
      )}
    </div>
  )
}
