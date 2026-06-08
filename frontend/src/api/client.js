import axios from 'axios'
import { parseAxiosError } from './errors'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(parseAxiosError(err))
  }
)

export const unwrap = async (promise) => {
  try {
    const res = await promise
    if (res.data?.success === false) {
      throw parseAxiosError({ response: { data: res.data, status: res.status } })
    }
    return res.data?.data ?? res.data
  } catch (err) {
    if (err.name === 'ApiError') throw err
    throw parseAxiosError(err)
  }
}

export default api
