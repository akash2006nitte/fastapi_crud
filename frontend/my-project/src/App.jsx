import { useEffect, useState } from 'react'
import './App.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function decodeJwtPayload(token) {
  try {
    const payload = token.split('.')[1]
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
    return JSON.parse(atob(padded))
  } catch {
    return null
  }
}

function App() {
  const [users, setUsers] = useState([])
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showNew, setShowNew] = useState(false)
  const [form, setForm] = useState({ user_id: '', image_url: '', caption: '' })
  const [token, setToken] = useState(localStorage.getItem('token') || null)
  const [showLogin, setShowLogin] = useState(false)
  const [showSignup, setShowSignup] = useState(false)
  const [loginForm, setLoginForm] = useState({ username: '', password: '' })
  const [signupForm, setSignupForm] = useState({ username: '', email: '', password: '' })
  const [file, setFile] = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const [uRes, pRes] = await Promise.all([fetch(`${API}/users/`), fetch(`${API}/posts/`)])
      const users = await uRes.json()
      const posts = await pRes.json()
      setUsers(users)
      setPosts(posts)
      setLoading(false)
    }
    load()
  }, [])

  const userMap = Object.fromEntries((users || []).map((u) => [u.id, u.username || u.name || '']))
  const currentUserId = token ? Number(decodeJwtPayload(token)?.sub) : null
  const currentUserLabel = currentUserId ? userMap[currentUserId] || `User #${currentUserId}` : ''

  async function submitNew(e) {
    e.preventDefault()
    let imageUrl = form.image_url
    // if file selected, upload first
    if (file) {
      const fd = new FormData()
      fd.append('file', file)
      const headers = token ? { Authorization: `Bearer ${token}` } : {}
      const up = await fetch(`${API}/media/upload`, { method: 'POST', body: fd, headers })
      if (!up.ok) return alert('Upload failed')
      const jd = await up.json()
      imageUrl = jd.url
    }

    const body = { user_id: currentUserId || undefined, image_url: imageUrl, caption: form.caption }
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`
    const res = await fetch(`${API}/posts/`, { method: 'POST', headers, body: JSON.stringify(body) })
    if (res.ok) {
      const newPost = await res.json()
      setPosts((p) => [newPost, ...p])
      setShowNew(false)
      setForm({ user_id: '', image_url: '', caption: '' })
      setFile(null)
    } else {
      alert('Failed to create post')
    }
  }

  async function doLogin(e) {
    e.preventDefault()
    const fd = new URLSearchParams()
    fd.append('username', loginForm.username)
    fd.append('password', loginForm.password)
    const res = await fetch(`${API}/auth/token`, { method: 'POST', body: fd })
    if (!res.ok) return alert('Login failed')
    const jd = await res.json()
    setToken(jd.access_token)
    localStorage.setItem('token', jd.access_token)
    setShowLogin(false)
  }

  async function doSignup(e) {
    e.preventDefault()
    const fd = new FormData()
    fd.append('username', signupForm.username)
    fd.append('email', signupForm.email)
    fd.append('password', signupForm.password)
    const params = new URLSearchParams()
    params.append('username', signupForm.username)
    params.append('email', signupForm.email)
    params.append('password', signupForm.password)
    const res = await fetch(`${API}/auth/register?${params.toString()}`, { method: 'POST', body: fd })
    if (!res.ok) return alert('Signup failed')
    setShowSignup(false)
    setShowLogin(true)
    setSignupForm({ username: '', email: '', password: '' })
    alert('Account created. You can sign in now.')
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>InstaClone</h1>
        <div className="top-actions">
          <button className="btn" onClick={() => setShowNew(true)}>New Post</button>
        </div>
      </header>

      <main className="container">
        <aside className="sidebar">
          <div className="profile-card">
            <h3>Users</h3>
            {users.map((u) => (
              <div key={u.id} className="user-line">{u.username || u.full_name || u.email}</div>
            ))}
            <div style={{marginTop:8}}>
              {!token ? (
                <div className="auth-actions">
                  <button className="btn" onClick={() => setShowLogin(true)}>Sign in</button>
                  <button className="btn muted" onClick={() => setShowSignup(true)}>Sign up</button>
                </div>
              ) : (
                <button className="btn" onClick={() => { setToken(null); localStorage.removeItem('token') }}>Logout</button>
              )}
            </div>
          </div>
          <div className="about">
            <h4>About</h4>
            <p>Simple Instagram-like frontend built for the FastAPI example.</p>
          </div>
        </aside>

        <section className="feed">
          {loading ? <div className="loader">Loading...</div> : posts.length === 0 ? <div>No posts yet</div> : null}
          {posts.map((post) => (
            <article key={post.id} className="post-card">
              <div className="post-header">
                <div className="avatar">{(userMap[post.user_id] || 'User')[0]?.toUpperCase()}</div>
                <div>
                  <div className="username">{userMap[post.user_id] || 'User'}</div>
                  <div className="meta">{new Date(post.created_at).toLocaleString()}</div>
                </div>
              </div>
              <div className="post-image">
                <img src={post.image_url} alt={post.caption || 'image'} />
              </div>
              <div className="post-body">
                <p className="caption"><strong>{userMap[post.user_id] || 'User'}</strong> {post.caption}</p>
              </div>
            </article>
          ))}
        </section>
      </main>

      {showNew && (
        <div className="modal">
          <form className="modal-card" onSubmit={submitNew}>
            <h3>New Post</h3>
            <div className="posting-as">
              <span className="posting-label">Posting as</span>
              <strong>{currentUserLabel || 'Sign in to post'}</strong>
            </div>
            <label>Image URL</label>
            <input value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} placeholder="https://..." />
            <label>Or upload image</label>
            <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
            <label>Caption</label>
            <textarea value={form.caption} onChange={(e) => setForm({ ...form, caption: e.target.value })} />
            <div className="modal-actions">
              <button type="button" className="btn muted" onClick={() => setShowNew(false)}>Cancel</button>
              <button type="submit" className="btn primary">Post</button>
            </div>
          </form>
        </div>
      )}

      {showLogin && (
        <div className="modal">
          <form className="modal-card" onSubmit={doLogin}>
            <h3>Sign in</h3>
            <label>Username or email</label>
            <input value={loginForm.username} onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })} required />
            <label>Password</label>
            <input type="password" value={loginForm.password} onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })} required />
            <div className="modal-actions">
              <button type="button" className="btn muted" onClick={() => setShowLogin(false)}>Cancel</button>
              <button type="submit" className="btn primary">Sign in</button>
            </div>
            <button type="button" className="btn muted" onClick={() => { setShowLogin(false); setShowSignup(true) }} style={{ marginTop: 12 }}>
              Need an account? Sign up
            </button>
          </form>
        </div>
      )}

      {showSignup && (
        <div className="modal">
          <form className="modal-card" onSubmit={doSignup}>
            <h3>Sign up</h3>
            <label>Username</label>
            <input value={signupForm.username} onChange={(e) => setSignupForm({ ...signupForm, username: e.target.value })} required />
            <label>Email</label>
            <input type="email" value={signupForm.email} onChange={(e) => setSignupForm({ ...signupForm, email: e.target.value })} required />
            <label>Password</label>
            <input type="password" value={signupForm.password} onChange={(e) => setSignupForm({ ...signupForm, password: e.target.value })} required />
            <div className="modal-actions">
              <button type="button" className="btn muted" onClick={() => setShowSignup(false)}>Cancel</button>
              <button type="submit" className="btn primary">Create account</button>
            </div>
            <button type="button" className="btn muted" onClick={() => { setShowSignup(false); setShowLogin(true) }} style={{ marginTop: 12 }}>
              Already have an account? Sign in
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

export default App
