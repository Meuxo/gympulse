import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { workoutAPI } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorState from '../components/common/ErrorState'

export default function WorkoutDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [workout, setWorkout] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    workoutAPI.get(id)
      .then((res) => setWorkout(res.data))
      .catch(() => setError('Workout not found'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorState message={error} />

  return (
    <div className="page">
      <button className="btn btn-ghost btn-sm mb-md" onClick={() => navigate(-1)}>Back</button>
      <h1 className="page-title mb-sm">{workout.title}</h1>
      <p className="text-sm text-2 mb-lg">{new Date(workout.date).toLocaleDateString('en', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>

      <div className="grid grid-3 mb-lg">
        <div className="card stat-card">
          <div className="stat-label">Type</div>
          <div className="font-semibold" style={{ fontSize: '1.05rem' }}>{workout.workout_type}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">Duration</div>
          <div className="stat-value">{workout.total_duration || 0}</div>
          <div className="stat-unit">min</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">Calories</div>
          <div className="stat-value">{workout.total_calories || 0}</div>
          <div className="stat-unit">kcal</div>
        </div>
      </div>

      {workout.muscle_groups?.length > 0 && (
        <div className="flex gap-xs flex-wrap mb-md">
          {workout.muscle_groups.map((mg) => <span key={mg} className="badge badge-primary">{mg.replace('_', ' ')}</span>)}
        </div>
      )}

      <div className="card mb-md">
        <div className="card-title">Exercises</div>
        {(!workout.exercises || workout.exercises.length === 0) ? (
          <p className="text-sm text-2">No exercises</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Exercise</th>
                <th style={{ textAlign: 'center' }}>Sets</th>
                <th style={{ textAlign: 'center' }}>Reps</th>
                <th style={{ textAlign: 'center' }}>Weight</th>
                <th style={{ textAlign: 'center' }}>Duration</th>
              </tr>
            </thead>
            <tbody>
              {workout.exercises.map((ex, i) => (
                <tr key={i}>
                  <td className="font-medium">{ex.name}</td>
                  <td style={{ textAlign: 'center' }}>{ex.sets || '—'}</td>
                  <td style={{ textAlign: 'center' }}>{ex.reps || '—'}</td>
                  <td style={{ textAlign: 'center' }}>{ex.weight ? `${ex.weight} lbs` : '—'}</td>
                  <td style={{ textAlign: 'center' }}>{ex.duration ? `${Math.round(ex.duration / 60)}m` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {workout.notes && (
        <div className="card">
          <div className="card-title">Notes</div>
          <p className="text-sm text-1">{workout.notes}</p>
        </div>
      )}
    </div>
  )
}
