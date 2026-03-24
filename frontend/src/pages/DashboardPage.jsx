import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { dashboardAPI, workoutAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorState from '../components/common/ErrorState'
import BusyLevelBadge from '../components/common/BusyLevelBadge'
import './DashboardPage.css'

const tooltipStyle = { background: 'var(--bg-2)', border: '1px solid var(--border)', borderRadius: 6, fontSize: '0.8rem' }

export default function DashboardPage() {
  const [summary, setSummary] = useState(null)
  const [weeklyWorkouts, setWeeklyWorkouts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [dashRes, workoutsRes] = await Promise.all([
        dashboardAPI.summary(),
        workoutAPI.list({ limit: 50 }),
      ])
      setSummary(dashRes.data)
      const days = []
      for (let i = 6; i >= 0; i--) {
        const d = new Date(); d.setDate(d.getDate() - i)
        const dateStr = d.toISOString().split('T')[0]
        const dayW = (workoutsRes.data.workouts || []).filter((w) => w.date?.split('T')[0] === dateStr)
        days.push({
          day: d.toLocaleDateString('en', { weekday: 'short' }),
          calories: dayW.reduce((s, w) => s + (w.total_calories || 0), 0),
          duration: dayW.reduce((s, w) => s + (w.total_duration || 0), 0),
        })
      }
      setWeeklyWorkouts(days)
    } catch { setError('Failed to load dashboard') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorState message={error} onRetry={fetchData} />

  const w = summary?.wearables || {}
  const wd = summary?.workouts || {}

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">{new Date().toLocaleDateString('en', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
      </div>

      {/* Stats row - mixed layout, not all boxed */}
      <div className="dash-stats">
        <div className="dash-stat-main card">
          <div className="stat-value" style={{ fontSize: '2rem' }}>{wd.count || 0}</div>
          <div className="stat-label">workouts today</div>
        </div>
        <div className="dash-stat-group">
          <div className="dash-stat-line">
            <span className="dash-stat-num">{Math.round(w.calories_burned || wd.total_calories || 0).toLocaleString()}</span>
            <span className="dash-stat-unit">kcal burned</span>
          </div>
          <div className="dash-stat-line">
            <span className="dash-stat-num">{(w.steps || 0).toLocaleString()}</span>
            <span className="dash-stat-unit">steps</span>
          </div>
          <div className="dash-stat-line">
            <span className="dash-stat-num">{Math.round(w.active_minutes || 0)}</span>
            <span className="dash-stat-unit">active min</span>
          </div>
        </div>
      </div>

      <div className="grid grid-2 mb-lg">
        <div className="card">
          <div className="card-title">Weekly calories</div>
          <ResponsiveContainer width="100%" height={170}>
            <BarChart data={weeklyWorkouts} barSize={18}>
              <XAxis dataKey="day" stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false} width={32} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: 'rgba(255,255,255,.03)' }} />
              <Bar dataKey="calories" fill="var(--primary)" radius={[3, 3, 0, 0]} name="Calories" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">Wearable data</div>
          <div>
            {[
              ['Heart Rate', w.heart_rate_avg ? `${w.heart_rate_avg} bpm` : '--'],
              ['Sleep', w.sleep_duration ? `${w.sleep_duration} hrs` : '--'],
              ['Distance', w.distance ? `${w.distance} mi` : '--'],
              ['Steps', (w.steps || 0).toLocaleString()],
            ].map(([label, val]) => (
              <div className="wearable-row" key={label}>
                <span className="label">{label}</span>
                <span className="font-medium">{val}</span>
              </div>
            ))}
          </div>
          <Link to="/wearables" className="btn btn-ghost btn-sm mt-md">View devices</Link>
        </div>
      </div>

      {summary?.gyms?.length > 0 && (
        <div className="card mb-lg">
          <div className="flex-between mb-sm">
            <div className="card-title" style={{ margin: 0 }}>Saved gyms</div>
            <Link to="/gyms" className="btn btn-ghost btn-sm">All gyms</Link>
          </div>
          <div className="grid grid-3">
            {summary.gyms.map((gym) => (
              <Link to={`/gyms/${gym.gym_id}`} key={gym.gym_id} className="card card-interactive gym-mini">
                <div className="gym-mini-name">{gym.name}</div>
                <div className="flex-between">
                  {gym.current_busy_level ? (
                    <BusyLevelBadge level={gym.current_busy_level} label={gym.busy_level_label} />
                  ) : (
                    <span className="text-xs text-3">No reports</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {summary?.basketball?.length > 0 && (
        <div className="card">
          <div className="flex-between mb-sm">
            <div className="card-title" style={{ margin: 0 }}>Basketball courts</div>
            <Link to="/basketball" className="btn btn-ghost btn-sm">All courts</Link>
          </div>
          <div className="grid grid-3">
            {summary.basketball.map((c) => (
              <div key={c.gym_id} className="card card-interactive">
                <div className="gym-mini-name">{c.name}</div>
                <div className="text-xs text-2 mt-xs">~{c.avg_player_count} players avg</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
