import { useState, useEffect } from 'react'
import { basketballAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import ErrorState from '../components/common/ErrorState'
import PopularTimes from '../components/common/PopularTimes'

export default function BasketballPage() {
  const [courts, setCourts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [reports, setReports] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ player_count: '', notes: '' })
  const [photo, setPhoto] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const fetchCourts = async () => {
    setLoading(true)
    try {
      const res = await basketballAPI.listCourts()
      setCourts(res.data.courts || [])
    } catch { setError('Failed to load courts') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchCourts() }, [])

  const selectCourt = async (court) => {
    setSelected(court)
    try {
      const res = await basketballAPI.getReports(court.id)
      setReports(res.data.reports || [])
    } catch { setReports([]) }
  }

  const submitReport = async (e) => {
    e.preventDefault()
    if (!selected || !form.player_count) return
    setSubmitting(true)
    try {
      const fd = new FormData()
      fd.append('gym_id', selected.id)
      fd.append('player_count', parseInt(form.player_count))
      if (form.notes) fd.append('notes', form.notes)
      if (photo) fd.append('photo', photo)
      await basketballAPI.submitReport(fd)
      setForm({ player_count: '', notes: '' })
      setPhoto(null)
      setShowForm(false)
      selectCourt(selected)
      fetchCourts()
    } catch { alert('Failed to submit') }
    finally { setSubmitting(false) }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorState message={error} onRetry={fetchCourts} />

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Basketball Courts</h1>
        <p className="page-subtitle">Find pickup games near you</p>
      </div>

      {courts.length === 0 && <EmptyState title="No courts" message="Add a gym with basketball court type" />}

      <div className="grid grid-2">
        <div>
          <div className="card-title mb-sm">Courts</div>
          <div className="grid gap-sm">
            {courts.map((c) => (
              <button
                key={c.id}
                className="card card-interactive"
                style={{
                  width: '100%', textAlign: 'left', border: 'none',
                  outline: selected?.id === c.id ? '2px solid var(--primary)' : 'none',
                }}
                onClick={() => selectCourt(c)}
              >
                <div className="font-semibold" style={{ fontSize: '0.9rem' }}>{c.name}</div>
                <div className="text-xs text-3">{c.address || 'No address'}</div>
                <div className="flex-between mt-sm">
                  {c.avg_player_count != null ? (
                    <span className="badge badge-green">~{c.avg_player_count} players</span>
                  ) : (
                    <span className="text-xs text-3">No reports</span>
                  )}
                  <span className="text-xs text-3">{c.recent_reports_count} reports</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div>
          {selected ? (
            <>
              <div className="flex-between mb-sm">
                <div className="card-title" style={{ margin: 0 }}>{selected.name}</div>
                <button className="btn btn-soft btn-sm" onClick={() => setShowForm(!showForm)}>
                  {showForm ? 'Cancel' : 'Report'}
                </button>
              </div>

              {/* Popular Times for court */}
              <div className="mb-md">
                <PopularTimes gymId={selected.id} />
              </div>

              {showForm && (
                <form onSubmit={submitReport} className="card mb-md">
                  <div className="form-group">
                    <label>Player count</label>
                    <input type="number" className="form-input" placeholder="How many?" min="0" max="100" value={form.player_count} onChange={(e) => setForm({ ...form, player_count: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Notes</label>
                    <input className="form-input" placeholder="Full court, 3v3, etc." value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Photo</label>
                    <input type="file" accept="image/*" className="form-input" onChange={(e) => setPhoto(e.target.files[0])} />
                  </div>
                  <button type="submit" className="btn btn-primary btn-sm" disabled={submitting}>
                    {submitting ? 'Submitting...' : 'Submit'}
                  </button>
                </form>
              )}

              <div className="card">
                <div className="card-title">Recent Reports</div>
                {reports.length === 0 ? (
                  <p className="text-sm text-2">No recent reports</p>
                ) : reports.map((r) => (
                  <div key={r.id} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                    <div className="flex-between">
                      <span>
                        <span className="font-semibold">{r.player_count} players</span>
                        <span className="text-xs text-2" style={{ marginLeft: 8 }}>{r.user_display_name}</span>
                      </span>
                      <span className="text-xs text-3">{new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    {r.notes && <p className="text-xs text-2 mt-xs">{r.notes}</p>}
                    {r.photo_url && <img src={r.photo_url} alt="Court" style={{ maxWidth: '100%', borderRadius: 8, marginTop: 8, maxHeight: 180, objectFit: 'cover' }} />}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="empty-state"><h3>Select a court</h3><p>Tap a court to see activity</p></div>
          )}
        </div>
      </div>
    </div>
  )
}
