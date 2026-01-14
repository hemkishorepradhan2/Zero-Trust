import React, { useState } from 'react'
import Login from './Login'
import Dashboard from './Dashboard'
import { getAccessToken, clearTokens, getUserFromToken } from './api'

export default function App() {
  const [loggedIn, setLoggedIn] = useState(!!getAccessToken())

  const user = loggedIn ? getUserFromToken() : null

  return (
    <div className="app-root">
      {!loggedIn ? (
        <Login onSuccess={() => setLoggedIn(true)} />
      ) : (
        <>
          <div className="topbar">
            <h1>AccessGuard — SOC Dashboard</h1>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              {user && <div style={{ color: '#9b5cff' }}>{user.username} • {user.role}</div>}
              <button
                onClick={() => {
                  clearTokens()
                  setLoggedIn(false)
                }}
              >
                Sign out
              </button>
            </div>
          </div>
          {user && user.role === 'admin' ? (
            <Dashboard />
          ) : (
            <div className="panel">
              <h2>Welcome to AccessGuard</h2>
              <p>You're logged in as <strong>{user?.username}</strong>. This is the user homepage with a simplified overview.</p>
              <ul>
                <li>Live risk: minimal view</li>
                <li>Request history: recent requests for your account</li>
                <li>Contact an admin to access the SOC dashboard</li>
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  )
}
