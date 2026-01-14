import React, { useEffect, useState, useRef } from 'react'
import { get, getAccessToken, postJSON } from './api'

function RiskMeter({ score }) {
  const color = score > 70 ? '#ff2e63' : score > 40 ? '#ffd66b' : '#7afcff'
  return (
    <div className="panel">
      <h4>Live Risk</h4>
      <div className="meter-bg">
        <div className="meter-fill" style={{ width: `${score}%`, background: color }} />
      </div>
      <div className="meter-label">Risk: {score}</div>
    </div>
  )
}

function DecisionBadge({ decision }) {
  if (!decision) return null
  return (
    <span className={
      decision.toLowerCase() === 'allow' ? 'decision-allow' : decision.toLowerCase() === 'deny' ? 'decision-deny' : 'decision-log'
    }>
      {decision}
    </span>
  )
}

export default function Dashboard() {
  const [logs, setLogs] = useState([])
  const [score, setScore] = useState(0)
  const [error, setError] = useState(null)
  const [tab, setTab] = useState('home')
  const streamRef = useRef([])
  const [uName, setUName] = useState('')
  const [uEmail, setUEmail] = useState('')
  const [uPass, setUPass] = useState('')
  const [uRole, setURole] = useState('user')
  const [adminMsg, setAdminMsg] = useState(null)

  async function fetchLogs() {
    try {
      const token = getAccessToken()
      const resp = await get('/admin/logs', token)
      if (resp && resp.status >= 200 && resp.status < 300 && Array.isArray(resp.data)) {
        setError(null)
        setLogs(resp.data)
        streamRef.current = resp.data.slice(0, 50)
        const max = resp.data.reduce((m, r) => Math.max(m, r.risk_score || 0), 0)
        setScore(max)
      } else {
        // backend returned error object
        setError((resp && (resp.data && (resp.data.detail || resp.data.error))) || `Status ${resp && resp.status}`)
        setLogs([])
      }
    } catch (e) {
      console.error(e)
      setError(e.message)
    }
  }

  useEffect(() => {
    fetchLogs()
    const id = setInterval(fetchLogs, 2500)
    return () => clearInterval(id)
  }, [])

  const recent = logs.slice(0, 30)
  const alerts = logs.filter((l) => l.suspicious).slice(0, 10)

  return (
    <div className="dashboard">
      <div className="controls">
        <div className="panel top-controls">
          <button onClick={() => setTab('home')}>Home</button>
          <button onClick={() => setTab('admin')}>Admin</button>
        </div>
        <RiskMeter score={score} />
        <div className="panel">
          <h4>Attack Detection</h4>
          {alerts.length === 0 ? <div>No alerts</div> : alerts.map(a => (
            <div key={a.id} className="stream-row">
              <div className="meta">
                <strong>{a.username || 'anon'}</strong>
                <span>{a.endpoint}</span>
                <DecisionBadge decision={a.decision} />
              </div>
              <div>{a.risk_score}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="panels">
        {tab === 'home' && (
          <>
            <div className="panel">
              <h3>Live Request Stream</h3>
              <div style={{ maxHeight: 300, overflow: 'auto' }}>
                {recent.map((l) => (
                  <div key={l.id} className="stream-row">
                    <div className="meta">
                      <div style={{ width: 220 }}><strong>{l.username || '—'}</strong> · <small>{l.role || 'n/a'}</small></div>
                      <div>{l.endpoint}</div>
                    </div>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                      <div style={{ width: 80 }}>{l.risk_score}</div>
                      <DecisionBadge decision={l.decision} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <h3>Risk Trends</h3>
              <svg width="100%" height="120">
                {logs.slice(0, 30).map((p, i) => {
                  const h = Math.min(100, p.risk_score || 0)
                  const x = (i / 30) * 100
                  return <rect key={i} x={`${x}%`} y={120 - h} width={`${100 / 30}%`} height={h} fill="#7afcff33" />
                })}
              </svg>
            </div>
          </>
        )}

        {tab === 'admin' && (
          <div className="panel logs">
            <h3>Audit Logs (Admin)</h3>
            {error && <div style={{ color: '#ff7b7b', marginBottom: 8 }}>Error: {error}</div>}
            <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
              <div style={{ flex: 1 }}>
                <h4>Create User</h4>
                <label>Username</label>
                <input value={uName} onChange={(e) => setUName(e.target.value)} />
                <label>Email</label>
                <input value={uEmail} onChange={(e) => setUEmail(e.target.value)} />
                <label>Password</label>
                <input type="password" value={uPass} onChange={(e) => setUPass(e.target.value)} />
                <label>Role</label>
                <select value={uRole} onChange={(e) => setURole(e.target.value)}>
                  <option value="user">user</option>
                  <option value="admin">admin</option>
                </select>
                <div style={{ marginTop: 8 }}>
                  <button onClick={async () => {
                    setAdminMsg(null)
                    try {
                      const resp = await postJSON('/admin/users/create', { username: uName, email: uEmail, password: uPass, role: uRole })
                      if (resp && resp.status >= 200 && resp.status < 300 && resp.data && resp.data.id) {
                        setAdminMsg(`Created user ${resp.data.username} (id ${resp.data.id})`)
                        setUName(''); setUEmail(''); setUPass(''); setURole('user')
                        fetchLogs()
                      } else {
                        setAdminMsg((resp && resp.data && (resp.data.detail || resp.data.error)) || `Status ${resp && resp.status}`)
                      }
                    } catch (err) {
                      setAdminMsg(err.message)
                    }
                  }}>Create</button>
                  {adminMsg && <div style={{ marginTop: 8 }}>{adminMsg}</div>}
                </div>
              </div>

              <div style={{ flex: 2 }}>
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>User</th>
                      <th>Event</th>
                      <th>Endpoint</th>
                      <th>Risk</th>
                      <th>Decision</th>
                      <th>IP</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((l) => (
                      <tr key={l.id} className={l.suspicious ? 'suspicious' : ''}>
                        <td>{l.id}</td>
                        <td>{l.username}</td>
                        <td>{l.event_type}</td>
                        <td>{l.endpoint}</td>
                        <td>{l.risk_score}</td>
                        <td><DecisionBadge decision={l.decision} /></td>
                        <td>{l.ip}</td>
                        <td>{l.timestamp}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="floating">AccessGuard • Live</div>
    </div>
  )
}
