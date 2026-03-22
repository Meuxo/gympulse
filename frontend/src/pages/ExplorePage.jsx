import { useState } from 'react'
import { gymAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'

const CITIES = [
  { name: 'New York', lat: 40.7128, lng: -74.0060 },
  { name: 'Los Angeles', lat: 34.0522, lng: -118.2437 },
  { name: 'Chicago', lat: 41.8781, lng: -87.6298 },
  { name: 'Houston', lat: 29.7604, lng: -95.3698 },
  { name: 'Miami', lat: 25.7617, lng: -80.1918 },
]

function StarRating({ rating }) {
  if (!rating) return null
  const full = Math.floor(rating)
  const half = rating - full >= 0.5
  const stars = []
  for (let i = 0; i < full; i++) stars.push('\u2605')
  if (half) stars.push('\u00BD')
  return (
    <span style={{ color: '#f5a623', fontSize: '0.85rem' }}>
      {stars.join('')} <span className="text-xs text-3">{rating.toFixed(1)}</span>
    </span>
  )
}

export default function ExplorePage() {
  const [query, setQuery] = useState('gym')
  const [lat, setLat] = useState('')
  const [lng, setLng] = useState('')
  const [radius, setRadius] = useState(5000)
  const [results, setResults] = useState([])
  const [source, setSource] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [importing, setImporting] = useState({})
  const [imported, setImported] = useState({})
  const [locationLabel, setLocationLabel] = useState('')

  const doSearch = async (searchLat, searchLng, label) => {
    if (!searchLat || !searchLng) {
      setError('Please select a city or use your location.')
      return
    }
    setLoading(true)
    setError(null)
    setResults([])
    setLocationLabel(label || '')
    try {
      const res = await gymAPI.searchNearby({
        q: query || 'gym',
        lat: searchLat,
        lng: searchLng,
        radius,
      })
      setResults(res.data.results || [])
      setSource(res.data.source || '')
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    doSearch(parseFloat(lat), parseFloat(lng), '')
  }

  const handleCityClick = (city) => {
    setLat(city.lat.toString())
    setLng(city.lng.toString())
    doSearch(city.lat, city.lng, city.name)
  }

  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.')
      return
    }
    setError(null)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const newLat = pos.coords.latitude
        const newLng = pos.coords.longitude
        setLat(newLat.toString())
        setLng(newLng.toString())
        doSearch(newLat, newLng, 'My Location')
      },
      () => setError('Could not get your location. Please allow location access or select a city.'),
    )
  }

  const handleImport = async (place) => {
    const key = place.google_place_id || place.name
    setImporting((prev) => ({ ...prev, [key]: true }))
    try {
      await gymAPI.importGoogle(place)
      setImported((prev) => ({ ...prev, [key]: true }))
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to import gym.')
    } finally {
      setImporting((prev) => ({ ...prev, [key]: false }))
    }
  }

  return (
    <div className="page">
      <div className="mb-lg">
        <h1 className="page-title">Explore Gyms</h1>
        <p className="page-subtitle">Search for any gym across the United States</p>
      </div>

      {/* Quick city selection */}
      <div className="card mb-lg">
        <div className="card-title" style={{ marginBottom: '0.75rem' }}>Quick Search by City</div>
        <div className="flex gap-sm flex-wrap">
          {CITIES.map((city) => (
            <button
              key={city.name}
              className="btn btn-ghost btn-sm"
              style={{
                border: '1px solid var(--border)',
                borderRadius: '100px',
                padding: '0.35rem 1rem',
                fontSize: '0.8rem',
              }}
              onClick={() => handleCityClick(city)}
            >
              {city.name}
            </button>
          ))}
          <button
            className="btn btn-primary btn-sm"
            style={{ borderRadius: '100px', padding: '0.35rem 1rem', fontSize: '0.8rem' }}
            onClick={handleUseMyLocation}
          >
            Use My Location
          </button>
        </div>
      </div>

      {/* Custom search form */}
      <form onSubmit={handleSearch} className="card mb-lg">
        <div className="card-title" style={{ marginBottom: '0.75rem' }}>Custom Search</div>
        <div className="grid grid-3 gap-sm" style={{ alignItems: 'end' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label>Search Query</label>
            <input
              className="form-input"
              placeholder='e.g. "CrossFit", "Planet Fitness", "yoga studio"'
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label>Latitude</label>
            <input
              className="form-input"
              type="number"
              step="any"
              placeholder="40.7128"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              required
            />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label>Longitude</label>
            <input
              className="form-input"
              type="number"
              step="any"
              placeholder="-74.0060"
              value={lng}
              onChange={(e) => setLng(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="flex gap-sm mt-md" style={{ alignItems: 'center' }}>
          <div className="form-group" style={{ margin: 0, maxWidth: '200px' }}>
            <label>Radius</label>
            <select
              className="form-input"
              value={radius}
              onChange={(e) => setRadius(Number(e.target.value))}
            >
              <option value={1000}>1 km</option>
              <option value={2000}>2 km</option>
              <option value={5000}>5 km</option>
              <option value={10000}>10 km</option>
              <option value={25000}>25 km</option>
              <option value={50000}>50 km</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary btn-sm" style={{ alignSelf: 'flex-end' }}>
            Search
          </button>
        </div>
      </form>

      {/* Status messages */}
      {source === 'database' && (
        <div className="card mb-lg" style={{ background: 'var(--bg-2)', border: '1px solid var(--border)' }}>
          <p className="text-xs text-3" style={{ margin: 0 }}>
            Google Places API key is not configured. Showing gyms from the GymPulse database instead.
            Ask your admin to add a GOOGLE_PLACES_API_KEY to enable full US gym search.
          </p>
        </div>
      )}

      {locationLabel && !loading && !error && (
        <p className="text-xs text-3 mb-sm">
          Showing results near <strong>{locationLabel}</strong>
          {results.length > 0 && <> &mdash; {results.length} gym{results.length !== 1 ? 's' : ''} found</>}
        </p>
      )}

      {/* Loading / Error states */}
      {loading && <LoadingSpinner />}
      {error && (
        <div className="card mb-lg" style={{ borderLeft: '3px solid var(--danger)' }}>
          <p style={{ margin: 0, color: 'var(--danger)' }}>{error}</p>
        </div>
      )}

      {/* Results grid */}
      {!loading && results.length > 0 && (
        <div className="grid grid-2">
          {results.map((place, idx) => {
            const key = place.google_place_id || place.id || `${place.name}-${idx}`
            const isImported = imported[place.google_place_id || place.name]
            const isImporting = importing[place.google_place_id || place.name]
            return (
              <div key={key} className="card">
                <div className="flex-between mb-xs">
                  <span className="font-semibold" style={{ fontSize: '0.95rem' }}>{place.name}</span>
                  <div className="flex gap-xs">
                    {place.is_open === true && (
                      <span className="badge badge-green">Open</span>
                    )}
                    {place.is_open === false && (
                      <span className="badge badge-red">Closed</span>
                    )}
                    {place.source === 'google' && (
                      <span className="badge badge-blue">Google</span>
                    )}
                  </div>
                </div>
                <div className="text-xs text-3 mb-sm">{place.address || 'No address'}</div>
                <div className="flex-between mb-sm">
                  <StarRating rating={place.rating} />
                  {place.rating_count && (
                    <span className="text-xs text-3">({place.rating_count} reviews)</span>
                  )}
                </div>
                {place.google_place_id && (
                  <button
                    className={`btn btn-sm ${isImported ? 'btn-ghost' : 'btn-primary'}`}
                    style={{ width: '100%' }}
                    disabled={isImporting || isImported}
                    onClick={() => handleImport(place)}
                  >
                    {isImported ? 'Added to GymPulse' : isImporting ? 'Adding...' : 'Add to GymPulse'}
                  </button>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && results.length === 0 && locationLabel && (
        <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-3)' }}>
          <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>No gyms found</p>
          <p className="text-xs">Try a different search query or increase the radius.</p>
        </div>
      )}
    </div>
  )
}
