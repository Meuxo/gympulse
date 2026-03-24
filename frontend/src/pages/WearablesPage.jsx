import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { wearableAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorState from '../components/common/ErrorState'

const tooltipStyle = { background: 'var(--bg-2)', border: '1px solid var(--border)', borderRadius: 8, fontSize: '0.8rem' }

const PROVIDERS = [
  { id: 'fitbit', name: 'Fitbit', desc: 'Sync via OAuth2 — connect your Fitbit account', badge: 'badge-green', web: true },
  { id: 'apple_health', name: 'Apple Health', desc: 'Available on the GymPulse mobile app (iOS)', badge: 'badge-blue', web: false },
  { id: 'samsung_health', name: 'Samsung Health', desc: 'Available on the GymPulse mobile app (Android)', badge: 'badge-yellow', web: false },
]

export default function WearablesPage() {
  const [weeklyData, setWeeklyData] = useState([])
  const [todaySummary, setTodaySummary] = useState({})
  const [connections, setConnections] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true); setError(null)
    try {
      const [connRes] = await Promise.all([
        wearableAPI.connections().catch(() => ({ data: { connections: [] } })),
      ])
      setConnections(connRes.data.connections || [])

      const days = []
      for (let i = 6; i >= 0; i--) {
        const d = new Date(); d.setDate(d.getDate() - i)
        const dateStr = d.toISOString().split('T')[0]
        try {
          const res = await wearableAPI.dailySummary(dateStr)
          days.push({ day: d.toLocaleDateString('en', { weekday: 'short' }), ...res.data })
        } catch {
          days.push({ day: d.toLocaleDateString('en', { weekday: 'short' }), date: dateStr })
        }
      }
      setWeeklyData(days)
      setTodaySummary(days[days.length - 1] || {})
    } catch { setError('Failed to load data') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [])

  const handleConnect = async (id) => {
    try {
      let res
      if (id === 'fitbit') {
        res = await wearableAPI.fitbitAuthorize()
        if (res.data.authorization_url) {
          window.location.href = res.data.authorization_url
          return
        }
      } else if (id === 'apple_health') res = await wearableAPI.appleHealthInfo()
      else res = await wearableAPI.samsungInfo()
      alert(res.data.message || JSON.stringify(res.data.instructions))
    } catch { alert('Connection failed') }
  }

  const handleFitbitSync = async () => {
    try {
      const res = await wearableAPI.fitbitSync()
      alert(res.data.message)
      fetchData()
    } catch (err) { alert(err.response?.data?.detail || 'Sync failed') }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorState message={error} onRetry={fetchData} />

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Connected Devices</h1>
        <p className="page-subtitle">Sync your wearable data</p>
      </div>

      <div className="grid grid-3 mb-lg">
        {PROVIDERS.map((p) => {
          const conn = connections.find((c) => c.provider === p.id)
          const connected = conn?.is_connected
          return (
            <div key={p.id} className="card">
              <div className="flex-between mb-xs">
                <span className="font-semibold">{p.name}</span>
                {p.web ? (
                  <span className={`badge ${connected ? 'badge-green' : p.badge}`}>
                    {connected ? 'Connected' : 'Available'}
                  </span>
                ) : (
                  <span className="text-xs text-3">Mobile only</span>
                )}
              </div>
              <p className="text-xs text-2 mb-sm">{p.desc}</p>
              {p.web ? (
                <div className="flex gap-xs">
                  <button className="btn btn-ghost btn-sm" onClick={() => handleConnect(p.id)}>
                    {connected ? 'Reconnect' : 'Connect'}
                  </button>
                  {connected && p.id === 'fitbit' && (
                    <button className="btn btn-soft btn-sm" onClick={handleFitbitSync}>Sync now</button>
                  )}
                </div>
              ) : (
                <p className="text-xs text-3" style={{ fontStyle: 'italic' }}>
                  Integration available in the mobile application
                </p>
              )}
            </div>
          )
        })}
      </div>

      <div className="grid grid-4 mb-lg">
        {[
          ['Steps', (todaySummary.steps || 0).toLocaleString(), null],
          ['Heart Rate', todaySummary.heart_rate_avg || '--', 'bpm'],
          ['Calories', Math.round(todaySummary.calories_burned || 0).toLocaleString(), 'kcal'],
          ['Sleep', todaySummary.sleep_duration || '--', 'hrs'],
        ].map(([label, val, unit]) => (
          <div key={label} className="card stat-card">
            <div className="stat-label">{label}</div>
            <div className="stat-value">{val}</div>
            {unit && <div className="stat-unit">{unit}</div>}
          </div>
        ))}
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-title">Steps — 7 Days</div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={weeklyData}>
              <XAxis dataKey="day" stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false} width={40} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="steps" stroke="var(--green)" strokeWidth={2} dot={{ r: 3, fill: 'var(--green)' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <div className="card-title">Calories — 7 Days</div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={weeklyData}>
              <XAxis dataKey="day" stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false} width={40} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="calories_burned" stroke="var(--accent)" strokeWidth={2} dot={{ r: 3, fill: 'var(--accent)' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
