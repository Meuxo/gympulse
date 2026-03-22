import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { workoutAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import ErrorState from '../components/common/ErrorState'

const TYPES = ['', 'strength', 'cardio', 'hiit', 'yoga', 'sports', 'flexibility', 'other']
const MUSCLES = ['', 'chest', 'back', 'shoulders', 'biceps', 'triceps', 'legs', 'glutes', 'core', 'full_body', 'cardio']

export default function WorkoutsPage() {
  const [workouts, setWorkouts] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ workout_type: '', muscle_group: '' })

  const fetchWorkouts = async () => {
    setLoading(true); setError(null)
    try {
      const params = {}
      if (filters.workout_type) params.workout_type = filters.workout_type
      if (filters.muscle_group) params.muscle_group = filters.muscle_group
      const res = await workoutAPI.list(params)
      setWorkouts(res.data.workouts || [])
      setTotal(res.data.total || 0)
    } catch { setError('Failed to load workouts') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchWorkouts() }, [])

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this workout?')) return
    try { await workoutAPI.delete(id); setWorkouts((p) => p.filter((w) => w.id !== id)) } catch {}
  }

  return (
    <div className="page">
      <div className="flex-between mb-lg">
        <div>
          <h1 className="page-title">Workouts</h1>
          <p className="page-subtitle">{total} total workouts logged</p>
        </div>
        <Link to="/workouts/new" className="btn btn-primary btn-sm">+ Log workout</Link>
      </div>

      <div className="card mb-lg">
        <div className="flex gap-sm flex-wrap" style={{ alignItems: 'end' }}>
          <select className="form-input" style={{ width: 160 }} value={filters.workout_type} onChange={(e) => setFilters({ ...filters, workout_type: e.target.value })}>
            {TYPES.map((t) => <option key={t} value={t}>{t || 'All types'}</option>)}
          </select>
          <select className="form-input" style={{ width: 160 }} value={filters.muscle_group} onChange={(e) => setFilters({ ...filters, muscle_group: e.target.value })}>
            {MUSCLES.map((m) => <option key={m} value={m}>{m || 'All muscles'}</option>)}
          </select>
          <button className="btn btn-ghost btn-sm" onClick={fetchWorkouts}>Filter</button>
        </div>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorState message={error} onRetry={fetchWorkouts} />}
      {!loading && !error && workouts.length === 0 && (
        <EmptyState title="No workouts" message="Start tracking" action={<Link to="/workouts/new" className="btn btn-primary btn-sm">Log first workout</Link>} />
      )}

      {!loading && workouts.length > 0 && (
        <div className="grid gap-sm">
          {workouts.map((w) => (
            <div key={w.id} className="card card-interactive" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Link to={`/workouts/${w.id}`} style={{ flex: 1, textDecoration: 'none', color: 'inherit' }}>
                <div className="flex-between">
                  <div>
                    <div className="font-semibold">{w.title}</div>
                    <div className="text-xs text-2 mt-xs">
                      <span className="badge badge-primary" style={{ marginRight: 4 }}>{w.workout_type}</span>
                      {w.muscle_groups?.slice(0, 3).map((m) => (
                        <span key={m} style={{ marginRight: 4, color: 'var(--text-3)', fontSize: '0.72rem' }}>{m}</span>
                      ))}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div className="text-xs text-3">{new Date(w.date).toLocaleDateString()}</div>
                    <div className="text-sm text-1 mt-xs">
                      {w.total_duration && <span>{w.total_duration}m</span>}
                      {w.total_calories && <span> · {w.total_calories} cal</span>}
                    </div>
                  </div>
                </div>
              </Link>
              <button className="btn btn-danger btn-sm hide-mobile" style={{ marginLeft: 12 }} onClick={() => handleDelete(w.id)}>Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
