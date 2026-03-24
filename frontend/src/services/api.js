import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
}

export const workoutAPI = {
  list: (params) => api.get('/workouts/', { params }),
  get: (id) => api.get(`/workouts/${id}`),
  create: (data) => api.post('/workouts/', data),
  update: (id, data) => api.put(`/workouts/${id}`, data),
  delete: (id) => api.delete(`/workouts/${id}`),
  stats: () => api.get('/workouts/stats/summary'),
}

export const wearableAPI = {
  syncData: (data) => api.post('/wearables/sync', data),
  syncBatch: (data) => api.post('/wearables/sync/batch', data),
  getData: (params) => api.get('/wearables/data', { params }),
  dailySummary: (date) => api.get('/wearables/daily-summary', { params: { date } }),
  connections: () => api.get('/wearables/connections'),
  fitbitAuthorize: () => api.get('/wearables/fitbit/authorize'),
  fitbitSync: () => api.post('/wearables/fitbit/sync'),
  appleHealthInfo: () => api.get('/wearables/apple-health/info'),
  samsungInfo: () => api.get('/wearables/samsung-health/info'),
}

export const gymAPI = {
  list: (params) => api.get('/gyms/', { params }),
  get: (id) => api.get(`/gyms/${id}`),
  create: (data) => api.post('/gyms/', data),
  update: (id, data) => api.put(`/gyms/${id}`, data),
  save: (id) => api.post(`/gyms/${id}/save`),
  unsave: (id) => api.delete(`/gyms/${id}/save`),
  submitCrowdReport: (gymId, data) => api.post(`/gyms/${gymId}/crowd-reports`, data),
  getCrowdReports: (gymId, params) => api.get(`/gyms/${gymId}/crowd-reports`, { params }),
  getPopularTimes: (gymId) => api.get(`/gyms/${gymId}/popular-times`),
  searchNearby: (params) => api.get('/gyms/search/nearby', { params }),
  searchByCity: (params) => api.get('/gyms/search/nearby', { params }),
  importGoogle: (data) => api.post('/gyms/import-google', data),
}

export const basketballAPI = {
  submitReport: (formData) => api.post('/basketball/reports', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getReports: (gymId, params) => api.get(`/basketball/reports/${gymId}`, { params }),
  listCourts: (params) => api.get('/basketball/courts', { params }),
}

export const dashboardAPI = {
  summary: () => api.get('/dashboard/summary'),
}

export const uploadAPI = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/uploads/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export default api
