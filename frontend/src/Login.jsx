import React, { useState } from 'react'
import { postJSON, postForm, saveTokens } from './api'

export default function Login({ onSuccess }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  async function doLogin(e) {
    e.preventDefault()
    try {
      // try OAuth2 token endpoint (form)
      const tokenResp = await postForm('/token', { username, password })
      if (tokenResp && tokenResp.status >= 200 && tokenResp.status < 300 && tokenResp.data && tokenResp.data.access_token) {
        saveTokens(tokenResp.data)
        setError(null)
        onSuccess()
        return
      }
      // fallback to JSON /login
      const jsonResp = await postJSON('/login', { username, password })
      if (jsonResp && jsonResp.status >= 200 && jsonResp.status < 300 && jsonResp.data && jsonResp.data.access_token) {
        saveTokens(jsonResp.data)
        setError(null)
        onSuccess()
        return
      }
      // surface error message from backend if available
      const msg = (tokenResp && tokenResp.data && (tokenResp.data.detail || tokenResp.data.error)) || (jsonResp && jsonResp.data && (jsonResp.data.detail || jsonResp.data.error)) || 'Login failed'
      setError(msg)
    } catch (err) {
      setError(err.message || 'Login error')
    }
  }

  return (
    <div className="login-panel">
      <h2>Sign in</h2>
      <form onSubmit={doLogin}>
        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} />
        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Sign in</button>
        {error && <div className="error">{error}</div>}
      </form>
    </div>
  )
}

