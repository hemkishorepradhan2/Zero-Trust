const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8080'

async function handleJsonResponse(res) {
  const text = await res.text()
  let payload
  try {
    payload = JSON.parse(text || 'null')
  } catch (e) {
    payload = { error: 'Invalid JSON response', raw: text }
  }
  return { status: res.status, data: payload }
}

export async function postJSON(path, body) {
  const token = localStorage.getItem('access_token')
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  return handleJsonResponse(res)
}

export async function postForm(path, formData) {
  const token = localStorage.getItem('access_token')
  const headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers,
    body: new URLSearchParams(formData),
  })
  return handleJsonResponse(res)
}

export async function get(path, token) {
  const t = token || localStorage.getItem('access_token')
  const headers = t ? { Authorization: `Bearer ${t}` } : {}
  const res = await fetch(`${API_BASE}${path}`, { headers })
  return handleJsonResponse(res)
}

export function saveTokens(data) {
  if (data.access_token) localStorage.setItem('access_token', data.access_token)
  if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
}

export function getAccessToken() {
  return localStorage.getItem('access_token')
}

export function getRefreshToken() {
  return localStorage.getItem('refresh_token')
}

export function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function refreshAccessToken() {
  const refresh_token = getRefreshToken()
  if (!refresh_token) return null
  const resp = await postJSON('/refresh', { refresh_token })
  if (resp && resp.status >= 200 && resp.status < 300 && resp.data && resp.data.access_token) {
    saveTokens(resp.data)
    return resp.data
  }
  return null
}

export function parseJwt(token) {
  if (!token) return null
  try {
    const parts = token.split('.')
    if (parts.length < 2) return null
    const payload = parts[1]
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decodeURIComponent(escape(decoded)))
  } catch (e) {
    return null
  }
}

export function getUserFromToken() {
  const t = getAccessToken()
  const p = parseJwt(t)
  if (!p) return null
  return { username: p.username, role: p.role }
}
