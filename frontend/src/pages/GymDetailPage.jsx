import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { gymAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorState from '../components/common/ErrorState'
import BusyLevelBadge from '../components/common/BusyLevelBadge'
import PopularTimes from '../components/common/PopularTimes'

const BUSY_OPTIONS = [
  { value: 1, label: 'Empty', color: 'var(--busy-1)' },
  { value: 2, label: 'Light', color: 'var(--busy-2)' },
  { value: 3, label: 'Moderate', color: 'var(--busy-3)' },
  { value: 4, label: 'Busy', color: 'var(--busy-4)' },
  { value: 5, label: 'Packed', color: 'var(--busy-5)' },
]

export default function GymDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [gym, setGym] = useState(null)
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedLevel, setSelectedLevel] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [gymRes, reportsRes] = await Promise.all([
        gymAPI.get(id),
        gymAPI.getCrowdReports(id, { hours: 4 }),
      ])
      setGym(gymRes.data)
      setReports(reportsRes.data.reports || [])
    } catch { setError('Failed to load gym') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [id])

  const submitReport = async () => {
    if (!selectedLevel) return
    setSubmitting(true)
    try {
      await gymAPI.submitCrowdReport(id, { gym_id: id, busy_level: selectedLevel })
      setSelectedLevel(null)
      fetchData()
    } catch { alert('Failed to submit') }
    finally { setSubmitting(false) }
  }

  const handleSave = async () => {
    try { await gymAPI.save(id); alert('Saved!') } catch { alert('Failed') }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorState message={error} />

  return (
    <div className="page">
      <button className="btn btn-ghost btn-sm mb-md" onClick={() => navigate(-1)}>Back</button>

      <div className="flex-between mb-lg">
        <div>
          <h1 className="page-title">{gym.name}</h1>
          <p className="text-sm text-2">{gym.address || 'No address'}</p>
          <div className="flex gap-xs mt-xs" style={{ alignItems: 'center' }}>
            <span className="badge badge-blue">{gym.gym_type}</span>
            {gym.google_rating && (
              <span className="text-xs text-2" style={{ marginLeft: 8 }}>
                &#9733; {gym.google_rating} ({gym.google_rating_count} reviews)
              </span>
            )}
          </div>
        </div>
        <button className="btn btn-soft btn-sm" onClick={handleSave}>Save gym</button>
      </div>

      {/* Current level */}
      <div className="card mb-md" style={{ textAlign: 'center', padding: 28 }}>
        <div className="text-xs text-2 mb-xs" style={{ textTransform: 'uppercase', letterSpacing: '.06em' }}>Current Crowd Level</div>
        {gym.current_busy_level ? (
          <>
            <div style={{ fontSize: '2.5rem', fontWeight: 700, lineHeight: 1.2 }}>{gym.current_busy_level}</div>
            <div className="mt-xs"><BusyLevelBadge level={gym.current_busy_level} label={gym.busy_level_label} /></div>
            <div className="text-xs text-3 mt-xs">
              {gym.data_source === 'google' ? 'Based on Google data' : `Based on ${gym.recent_reports_count} recent reports`}
            </div>
          </>
        ) : (
          <div className="text-2 mt-sm">No reports yet</div>
        )}
      </div>

      {/* Popular Times */}
      <div className="mb-md">
        <PopularTimes gymId={id} />
      </div>

      {/* Submit */}
      <div className="card mb-md">
        <div className="card-title">How busy is it?</div>
        <div className="flex gap-xs mb-md flex-wrap">
          {BUSY_OPTIONS.map((o) => (
            <button
              key={o.value}
              className={`btn btn-sm ${selectedLevel === o.value ? '' : 'btn-ghost'}`}
              style={selectedLevel === o.value ? { background: o.color, color: '#0b0e14', borderColor: o.color } : {}}
              onClick={() => setSelectedLevel(o.value)}
            >{o.label}</button>
          ))}
        </div>
        <button className="btn btn-primary btn-sm" disabled={!selectedLevel || submitting} onClick={submitReport}>
          {submitting ? 'Submitting...' : 'Submit report'}
        </button>
      </div>

      {/* Reports */}
      <div className="card mb-md">
        <div className="card-title">Recent Reports</div>
        {reports.length === 0 ? (
          <p className="text-2 text-sm">No reports in the last few hours</p>
        ) : reports.map((r) => (
          <div key={r.id} className="flex-between" style={{ padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
            <div className="flex gap-sm" style={{ alignItems: 'center' }}>
              <BusyLevelBadge level={r.busy_level} label={r.busy_level_label} />
              <span className="text-sm text-1">{r.user_display_name}</span>
            </div>
            <span className="text-xs text-3">{new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        ))}
      </div>

      {gym.amenities?.length > 0 && (
        <div className="card">
          <div className="card-title">Amenities</div>
          <div className="flex gap-xs flex-wrap">
            {gym.amenities.map((a) => <span key={a} className="badge badge-blue">{a}</span>)}
          </div>
        </div>
      )}
    </div>
  )
}
