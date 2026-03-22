import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { gymAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import ErrorState from '../components/common/ErrorState'
import BusyLevelBadge from '../components/common/BusyLevelBadge'

export default function GymsPage() {
  const [gyms, setGyms] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [newGym, setNewGym] = useState({ name: '', address: '', gym_type: 'gym' })

  const fetchGyms = async () => {
    setLoading(true); setError(null)
    try {
      const res = await gymAPI.list({ search: search || undefined, limit: 50 })
      setGyms(res.data.gyms || [])
    } catch { setError('Failed to load gyms') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchGyms() }, [])

  const handleSearch = (e) => { e.preventDefault(); fetchGyms() }

  const handleAddGym = async (e) => {
    e.preventDefault()
    try {
      await gymAPI.create(newGym)
      setNewGym({ name: '', address: '', gym_type: 'gym' })
      setShowAdd(false)
      fetchGyms()
    } catch (err) { alert(err.response?.data?.detail || 'Failed') }
  }

  return (
    <div className="page">
      <div className="flex-between mb-lg">
        <div>
          <h1 className="page-title">Gyms</h1>
          <p className="page-subtitle">Real-time crowd levels at gyms near you</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowAdd(!showAdd)}>
          {showAdd ? 'Cancel' : '+ Add gym'}
        </button>
      </div>

      {showAdd && (
        <form onSubmit={handleAddGym} className="card mb-lg">
          <div className="card-title">Add Gym</div>
          <div className="grid grid-3 gap-sm" style={{ alignItems: 'end' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label>Name</label>
              <input className="form-input" placeholder="Gym name" value={newGym.name} onChange={(e) => setNewGym({ ...newGym, name: e.target.value })} required />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label>Address</label>
              <input className="form-input" placeholder="123 Main St" value={newGym.address} onChange={(e) => setNewGym({ ...newGym, address: e.target.value })} />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label>Type</label>
              <select className="form-input" value={newGym.gym_type} onChange={(e) => setNewGym({ ...newGym, gym_type: e.target.value })}>
                <option value="gym">Gym</option>
                <option value="basketball_court">Basketball Court</option>
                <option value="both">Both</option>
              </select>
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-sm mt-md">Add</button>
        </form>
      )}

      <form onSubmit={handleSearch} className="flex gap-sm mb-lg">
        <input className="form-input" style={{ flex: 1 }} placeholder="Search gyms..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <button type="submit" className="btn btn-ghost">Search</button>
      </form>

      {loading && <LoadingSpinner />}
      {error && <ErrorState message={error} onRetry={fetchGyms} />}
      {!loading && !error && gyms.length === 0 && <EmptyState title="No gyms found" message="Try a different search or add one" />}

      {!loading && gyms.length > 0 && (
        <div className="grid grid-2">
          {gyms.map((gym) => (
            <Link to={`/gyms/${gym.id}`} key={gym.id} className="card card-interactive" style={{ textDecoration: 'none', color: 'inherit' }}>
              <div className="flex-between mb-xs">
                <span className="font-semibold" style={{ fontSize: '0.95rem' }}>{gym.name}</span>
                <span className="badge badge-blue">{gym.gym_type.replace('_', ' ')}</span>
              </div>
              <div className="text-xs text-3 mb-sm">{gym.address || 'No address'}</div>
              <div className="flex-between">
                {gym.current_busy_level ? (
                  <div className="flex gap-xs" style={{ alignItems: 'center' }}>
                    <BusyLevelBadge level={gym.current_busy_level} label={gym.busy_level_label} />
                    {gym.data_source === 'google' && <span className="text-xs" style={{ color: 'var(--accent)' }}>Google</span>}
                  </div>
                ) : (
                  <span className="text-xs text-3">No recent reports</span>
                )}
                <span className="text-xs text-3">
                  {gym.google_rating ? `★ ${gym.google_rating}` : `${gym.recent_reports_count} reports`}
                </span>
              </div>
              {gym.amenities?.length > 0 && (
                <div className="flex gap-xs flex-wrap mt-sm">
                  {gym.amenities.slice(0, 4).map((a) => (
                    <span key={a} style={{ fontSize: '0.65rem', color: 'var(--text-3)', background: 'var(--bg-3)', padding: '2px 7px', borderRadius: 100 }}>{a}</span>
                  ))}
                  {gym.amenities.length > 4 && <span style={{ fontSize: '0.65rem', color: 'var(--text-3)' }}>+{gym.amenities.length - 4}</span>}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
