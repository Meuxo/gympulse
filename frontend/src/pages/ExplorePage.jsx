import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { gymAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import BusyLevelBadge from '../components/common/BusyLevelBadge'

const MN_CITIES = [
  { name: 'Minneapolis', label: 'Minneapolis' },
  { name: 'St. Paul', label: 'St. Paul' },
  { name: 'Bloomington', label: 'Bloomington' },
  { name: 'Rochester', label: 'Rochester' },
  { name: 'Duluth', label: 'Duluth' },
  { name: 'Brooklyn Park', label: 'Brooklyn Park' },
  { name: 'Plymouth', label: 'Plymouth' },
  { name: 'Eagan', label: 'Eagan' },
  { name: 'Woodbury', label: 'Woodbury' },
  { name: 'Maple Grove', label: 'Maple Grove' },
]

export default function ExplorePage() {
  const [city, setCity] = useState('')
  const [query, setQuery] = useState('')
  const [radius, setRadius] = useState(10)
  const [gymType, setGymType] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchLabel, setSearchLabel] = useState('')

  const doSearch = async (searchCity, label) => {
    setLoading(true)
    setError(null)
    setResults([])
    setSearchLabel(label || searchCity || 'Minnesota')
    try {
      const res = await gymAPI.searchNearby({
        city: searchCity || '',
        q: query || '',
        radius,
        gym_type: gymType || undefined,
      })
      setResults(res.data.results || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  // Load all MN gyms on first visit
  useEffect(() => { doSearch('', 'All Minnesota') }, [])

  const handleCityClick = (c) => {
    setCity(c.name)
    doSearch(c.name, c.label)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    doSearch(city, city || 'All Minnesota')
  }

  return (
    <div className="page">
      <div className="mb-lg">
        <h1 className="page-title">Explore gyms</h1>
        <p className="page-subtitle">Find gyms and courts across Minnesota</p>
      </div>

      {/* City quick links */}
      <div className="mb-lg">
        <div className="text-xs text-2 mb-xs">Quick search by city</div>
        <div className="flex gap-xs flex-wrap">
          {MN_CITIES.map((c) => (
            <button
              key={c.name}
              className={`btn btn-sm ${city === c.name ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => handleCityClick(c)}
            >
              {c.label}
            </button>
          ))}
          <button
            className={`btn btn-sm ${city === '' && searchLabel === 'All Minnesota' ? 'btn-primary' : 'btn-soft'}`}
            onClick={() => { setCity(''); doSearch('', 'All Minnesota') }}
          >
            Show all
          </button>
        </div>
      </div>

      {/* Search form */}
      <form onSubmit={handleSearch} className="card mb-lg">
        <div className="card-title">Search</div>
        <div className="grid grid-3 gap-sm" style={{ alignItems: 'end' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label>City</label>
            <input
              className="form-input"
              placeholder="Minneapolis, St. Paul..."
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label>Name</label>
            <input
              className="form-input"
              placeholder="Planet Fitness, YMCA..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label>Type</label>
            <select
              className="form-input"
              value={gymType}
              onChange={(e) => setGymType(e.target.value)}
            >
              <option value="">All types</option>
              <option value="gym">Gym</option>
              <option value="basketball_court">Basketball court</option>
              <option value="both">Both</option>
            </select>
          </div>
        </div>
        <div className="flex gap-sm mt-md" style={{ alignItems: 'center' }}>
          <div className="form-group" style={{ margin: 0, maxWidth: '160px' }}>
            <label>Radius</label>
            <select
              className="form-input"
              value={radius}
              onChange={(e) => setRadius(Number(e.target.value))}
            >
              <option value={5}>5 miles</option>
              <option value={10}>10 miles</option>
              <option value={25}>25 miles</option>
              <option value={50}>50 miles</option>
              <option value={100}>100 miles</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary btn-sm" style={{ alignSelf: 'flex-end' }}>
            Search
          </button>
        </div>
      </form>

      {/* Results label */}
      {searchLabel && !loading && !error && (
        <p className="text-xs text-2 mb-sm">
          {searchLabel} &mdash; {results.length} found
        </p>
      )}

      {loading && <LoadingSpinner />}
      {error && <div className="error-state mb-md">{error}</div>}

      {/* Results grid */}
      {!loading && results.length > 0 && (
        <div className="grid grid-2">
          {results.map((gym) => (
            <Link
              to={`/gyms/${gym.id}`}
              key={gym.id}
              className="card card-interactive"
              style={{ textDecoration: 'none', color: 'inherit' }}
            >
              <div className="flex-between mb-xs">
                <span className="font-semibold" style={{ fontSize: '0.92rem' }}>{gym.name}</span>
                <span className="text-xs text-2">{(gym.gym_type || '').replace('_', ' ')}</span>
              </div>
              {gym.address && <div className="text-xs text-3 mb-sm">{gym.address}</div>}
              <div className="flex-between">
                {gym.current_busy_level ? (
                  <BusyLevelBadge level={gym.current_busy_level} label={gym.busy_level_label} />
                ) : (
                  <span className="text-xs text-3">No reports yet</span>
                )}
                {gym.google_rating && (
                  <span className="text-xs text-3">{gym.google_rating} stars</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}

      {!loading && !error && results.length === 0 && searchLabel && (
        <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-3)' }}>
          <p style={{ fontSize: '0.95rem', marginBottom: '0.4rem' }}>No gyms found</p>
          <p className="text-xs">Try a different city or search term.</p>
        </div>
      )}
    </div>
  )
}
