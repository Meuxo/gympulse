import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { workoutAPI } from '../services/api'

const TYPES = ['strength', 'cardio', 'hiit', 'yoga', 'sports', 'flexibility', 'other']
const MUSCLES = ['chest', 'back', 'shoulders', 'biceps', 'triceps', 'legs', 'glutes', 'core', 'full_body', 'cardio']
const emptyEx = { name: '', sets: '', reps: '', weight: '', duration: '', calories: '', notes: '' }

export default function NewWorkoutPage() {
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    title: '', workout_type: 'strength', muscle_groups: [],
    exercises: [{ ...emptyEx }], total_duration: '', total_calories: '', notes: '',
  })

  const toggleMuscle = (mg) => {
    setForm((p) => ({
      ...p, muscle_groups: p.muscle_groups.includes(mg) ? p.muscle_groups.filter((m) => m !== mg) : [...p.muscle_groups, mg],
    }))
  }

  const updateEx = (i, field, val) => {
    setForm((p) => { const ex = [...p.exercises]; ex[i] = { ...ex[i], [field]: val }; return { ...p, exercises: ex } })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) { setError('Title required'); return }
    setSaving(true); setError('')
    try {
      await workoutAPI.create({
        title: form.title, workout_type: form.workout_type, muscle_groups: form.muscle_groups,
        exercises: form.exercises.filter((ex) => ex.name.trim()).map((ex) => ({
          name: ex.name,
          sets: ex.sets ? parseInt(ex.sets) : null,
          reps: ex.reps ? parseInt(ex.reps) : null,
          weight: ex.weight ? parseFloat(ex.weight) : null,
          duration: ex.duration ? parseInt(ex.duration) * 60 : null,
          calories: ex.calories ? parseFloat(ex.calories) : null,
          notes: ex.notes || null,
        })),
        total_duration: form.total_duration ? parseInt(form.total_duration) : null,
        total_calories: form.total_calories ? parseFloat(form.total_calories) : null,
        notes: form.notes || null,
      })
      navigate('/workouts')
    } catch (err) { setError(err.response?.data?.detail || 'Failed') }
    finally { setSaving(false) }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Log Workout</h1>
      </div>

      {error && <div className="error-state mb-md">{error}</div>}

      <form onSubmit={handleSubmit} style={{ maxWidth: 700 }}>
        <div className="card mb-md">
          <div className="form-group">
            <label>Title</label>
            <input className="form-input" placeholder="e.g. Morning Push Day" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          </div>
          <div className="grid grid-2">
            <div className="form-group">
              <label>Type</label>
              <select className="form-input" value={form.workout_type} onChange={(e) => setForm({ ...form, workout_type: e.target.value })}>
                {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Duration (min)</label>
              <input type="number" className="form-input" placeholder="45" value={form.total_duration} onChange={(e) => setForm({ ...form, total_duration: e.target.value })} />
            </div>
          </div>
          <div className="form-group">
            <label>Muscle Groups</label>
            <div className="flex gap-xs flex-wrap">
              {MUSCLES.map((mg) => (
                <button key={mg} type="button" className={`btn btn-sm ${form.muscle_groups.includes(mg) ? 'btn-primary' : 'btn-ghost'}`} onClick={() => toggleMuscle(mg)}>
                  {mg.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="card mb-md">
          <div className="flex-between mb-md">
            <div className="card-title" style={{ margin: 0 }}>Exercises</div>
            <button type="button" className="btn btn-soft btn-sm" onClick={() => setForm((p) => ({ ...p, exercises: [...p.exercises, { ...emptyEx }] }))}>+ Add</button>
          </div>
          {form.exercises.map((ex, i) => (
            <div key={i} style={{ padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <div className="flex gap-sm mb-sm" style={{ alignItems: 'center' }}>
                <input className="form-input" style={{ flex: 1 }} placeholder="Exercise name" value={ex.name} onChange={(e) => updateEx(i, 'name', e.target.value)} />
                {form.exercises.length > 1 && (
                  <button type="button" className="btn btn-danger btn-sm" onClick={() => setForm((p) => ({ ...p, exercises: p.exercises.filter((_, j) => j !== i) }))}>Remove</button>
                )}
              </div>
              <div className="grid grid-4 gap-xs">
                <input type="number" className="form-input" placeholder="Sets" value={ex.sets} onChange={(e) => updateEx(i, 'sets', e.target.value)} />
                <input type="number" className="form-input" placeholder="Reps" value={ex.reps} onChange={(e) => updateEx(i, 'reps', e.target.value)} />
                <input type="number" className="form-input" placeholder="Weight" value={ex.weight} onChange={(e) => updateEx(i, 'weight', e.target.value)} />
                <input type="number" className="form-input" placeholder="Min" value={ex.duration} onChange={(e) => updateEx(i, 'duration', e.target.value)} />
              </div>
            </div>
          ))}
        </div>

        <div className="card mb-md">
          <div className="grid grid-2">
            <div className="form-group">
              <label>Total Calories</label>
              <input type="number" className="form-input" placeholder="300" value={form.total_calories} onChange={(e) => setForm({ ...form, total_calories: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Notes</label>
              <textarea className="form-input" rows={2} placeholder="How was it?" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            </div>
          </div>
        </div>

        <div className="flex gap-sm">
          <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Save workout'}</button>
          <button type="button" className="btn btn-ghost" onClick={() => navigate(-1)}>Cancel</button>
        </div>
      </form>
    </div>
  )
}
