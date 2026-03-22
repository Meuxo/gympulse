import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../services/api'

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const [displayName, setDisplayName] = useState(user?.display_name || '')
  const [units, setUnits] = useState('imperial')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true); setMessage('')
    try {
      await authAPI.updateMe({ display_name: displayName, preferences: { units, notifications_enabled: true } })
      setMessage('Saved')
    } catch { setMessage('Failed') }
    finally { setSaving(false) }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Profile</h1>
      </div>

      <div style={{ maxWidth: 440 }}>
        <div className="card mb-md">
          <form onSubmit={handleSave}>
            <div className="form-group">
              <label>Email</label>
              <input className="form-input" value={user?.email || ''} disabled style={{ opacity: 0.5 }} />
            </div>
            <div className="form-group">
              <label>Display Name</label>
              <input className="form-input" value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Units</label>
              <select className="form-input" value={units} onChange={(e) => setUnits(e.target.value)}>
                <option value="imperial">Imperial (lbs, mi)</option>
                <option value="metric">Metric (kg, km)</option>
              </select>
            </div>
            {message && <p className={`text-sm mb-sm ${message === 'Saved' ? 'text-green' : 'text-red'}`}>{message}</p>}
            <button type="submit" className="btn btn-primary btn-sm" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
          </form>
        </div>

        <div className="card">
          <div className="card-title">Account</div>
          <p className="text-sm text-2 mb-md">
            Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
          </p>
          <button className="btn btn-danger btn-sm" onClick={logout}>Sign out</button>
        </div>
      </div>
    </div>
  )
}
