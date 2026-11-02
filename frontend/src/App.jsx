
import { useEffect, useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'
const TOKEN_KEY = 'bookleaf_access_token'

async function apiRequest(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY)

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`)
  }

  return data
}

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [account, setAccount] = useState(null)

  async function handleLogin(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })

      if (!data.access_token) {
        throw new Error('The server did not return an access token.')
      }

      localStorage.setItem(TOKEN_KEY, data.access_token)

      const profile = await apiRequest('/api/auth/me')

      setAccount({
        ...profile,
        email: profile.email || data.user?.email || email,
        role: profile.role || data.role || 'author',
      })

      setPassword('')
    } catch (err) {
      localStorage.removeItem(TOKEN_KEY)
      setError(err.message || 'Unable to connect to the server.')
    } finally {
      setLoading(false)
    }
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_KEY)
    setAccount(null)
    setEmail('')
    setPassword('')
    setError('')
  }

  if (account) {
    if (account.role !== 'author') {
      return (
        <main className="portal">
          <header className="topbar">
            <div className="brand">
              <span className="brand-mark">B</span>
              <span>BookLeaf</span>
            </div>
            <button className="logout-button" onClick={handleLogout}>
              Log out
            </button>
          </header>
          <section className="welcome-card">
            <p className="eyebrow">BOOKLEAF PORTAL</p>
            <h1>Welcome back!</h1>
            <p className="welcome-description">
              Signed in as {account.email}. Your account role is {account.role}.
              The Admin Dashboard will be implemented in the next phase.
            </p>
          </section>
        </main>
      )
    }

    return (
      <AuthorDashboard account={account} onLogout={handleLogout} />
    )
  }

  return (
    <main className="login-page">
      <section className="login-visual">
        <div className="visual-brand">
          <span className="brand-mark">B</span>
          <span>BookLeaf</span>
        </div>

        <div className="visual-content">
          <div className="book-illustration" aria-hidden="true">
            <div className="book book-back" />
            <div className="book book-front">
              <span className="book-leaf">B</span>
            </div>
            <span className="spark spark-one">✦</span>
            <span className="spark spark-two">✧</span>
          </div>

          <p className="visual-kicker">AUTHOR SUPPORT PORTAL</p>
          <h1>Your stories deserve the best support.</h1>
          <p className="visual-description">
            Manage your books, track royalties and stay connected with the
            BookLeaf support team, all in one place.
          </p>
        </div>

        <footer className="visual-footer">
          Your publishing journey, made simpler.
        </footer>
      </section>

      <section className="login-panel">
        <div className="mobile-brand">
          <span className="brand-mark">B</span>
          <span>BookLeaf</span>
        </div>

        <div className="login-card">
          <p className="eyebrow">WELCOME TO BOOKLEAF</p>
          <h2>Sign in to your account</h2>
          <p className="login-subtitle">
            Enter your account details to continue to your portal.
          </p>

          <form onSubmit={handleLogin}>
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              autoComplete="username"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />

            <div className="password-label">
              <label htmlFor="password">Password</label>
            </div>

            <input
              id="password"
              type="password"
              autoComplete="current-password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />

            {error && (
              <div className="error-message" role="alert">
                {error}
              </div>
            )}

            <button className="login-button" type="submit" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
              {!loading && <span aria-hidden="true"> →</span>}
            </button>
          </form>

          <div className="secure-note">
            <span aria-hidden="true">⌑</span>
            Your account information is handled securely.
          </div>
        </div>

        <footer className="login-footer">
          Need help? Contact your BookLeaf support team.
        </footer>
      </section>
    </main>
  )
}

function AuthorDashboard({ account, onLogout }) {
  const [books, setBooks] = useState([])
  const [tickets, setTickets] = useState([])
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [replies, setReplies] = useState([])
  const [replyMessage, setReplyMessage] = useState('')
  const [showTicketForm, setShowTicketForm] = useState(false)
  const [ticketForm, setTicketForm] = useState({
    subject: '',
    description: '',
    category: 'General',
    book_id: '',
  })
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [activeTab, setActiveTab] = useState('overview')

  async function loadDashboard() {
    setLoading(true)
    setError('')

    try {
      const [bookData, ticketData] = await Promise.all([
        apiRequest('/api/author/books'),
        apiRequest('/api/author/tickets'),
      ])

      setBooks(Array.isArray(bookData) ? bookData : [])
      setTickets(Array.isArray(ticketData) ? ticketData : [])
    } catch (err) {
      setError(err.message || 'Unable to load dashboard information.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  async function openTicket(ticket) {
    setSelectedTicket(ticket)
    setReplies([])
    setError('')
    setNotice('')
    setActiveTab('tickets')

    try {
      const data = await apiRequest(
        `/api/author/tickets/${ticket.ticket_id}/replies`,
      )
      setReplies(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Unable to load ticket conversation.')
    }
  }

  async function submitTicket(event) {
    event.preventDefault()
    setActionLoading(true)
    setError('')
    setNotice('')

    try {
      await apiRequest('/api/author/tickets', {
        method: 'POST',
        body: JSON.stringify({
          subject: ticketForm.subject,
          description: ticketForm.description,
          category: ticketForm.category,
          book_id: ticketForm.book_id ? Number(ticketForm.book_id) : null,
        }),
      })

      setTicketForm({
        subject: '',
        description: '',
        category: 'General',
        book_id: '',
      })
      setShowTicketForm(false)
      setNotice('Your support ticket has been created.')
      await loadDashboard()
      setActiveTab('tickets')
    } catch (err) {
      setError(err.message || 'Unable to create ticket.')
    } finally {
      setActionLoading(false)
    }
  }

  async function submitReply(event) {
    event.preventDefault()

    if (!selectedTicket || !replyMessage.trim()) return

    setActionLoading(true)
    setError('')
    setNotice('')

    try {
      await apiRequest(
        `/api/author/tickets/${selectedTicket.ticket_id}/replies`,
        {
          method: 'POST',
          body: JSON.stringify({ message: replyMessage.trim() }),
        },
      )

      setReplyMessage('')
      const data = await apiRequest(
        `/api/author/tickets/${selectedTicket.ticket_id}/replies`,
      )
      setReplies(Array.isArray(data) ? data : [])
      setNotice('Your reply has been sent.')
      await loadDashboard()
    } catch (err) {
      setError(err.message || 'Unable to send reply.')
    } finally {
      setActionLoading(false)
    }
  }

  const openCount = tickets.filter(
    (ticket) => !['Closed', 'Resolved'].includes(ticket.status),
  ).length

  const pendingRoyalty = books.reduce(
    (total, book) => total + (Number(book.royalty_pending) || 0),
    0,
  )

  return (
    <main className="portal dashboard">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">B</span>
          <span>BookLeaf</span>
        </div>

        <div className="topbar-right">
          <span className="user-email">{account.email}</span>
          <button className="logout-button" onClick={onLogout}>
            Log out
          </button>
        </div>
      </header>

      <div className="dashboard-layout">
        <aside className="sidebar">
          <p className="sidebar-label">WORKSPACE</p>
          {[
            ['overview', 'Overview', '⌂'],
            ['books', 'My Books', '▤'],
            ['tickets', 'Support Tickets', '✉'],
          ].map(([tab, label, icon]) => (
            <button
              key={tab}
              className={`nav-item ${activeTab === tab ? 'active' : ''}`}
              onClick={() => {
                setActiveTab(tab)
                setSelectedTicket(null)
                setError('')
                setNotice('')
              }}
            >
              <span>{icon}</span>
              {label}
              {tab === 'tickets' && tickets.length > 0 && (
                <span className="nav-count">{tickets.length}</span>
              )}
            </button>
          ))}

          <div className="sidebar-account">
            <div className="avatar">
              {(account.email || 'A').charAt(0).toUpperCase()}
            </div>
            <div>
              <strong>Author Account</strong>
              <span>{account.email}</span>
            </div>
          </div>
        </aside>

        <section className="dashboard-main">
          <div className="page-heading">
            <div>
              <p className="eyebrow">AUTHOR WORKSPACE</p>
              <h1>
                {activeTab === 'overview'
                  ? 'Welcome back!'
                  : activeTab === 'books'
                    ? 'My Books'
                    : 'Support Tickets'}
              </h1>
              <p className="page-subtitle">
                {activeTab === 'overview'
                  ? 'Here is an overview of your publishing activity.'
                  : activeTab === 'books'
                    ? 'View your published and ongoing books.'
                    : 'Create a support request or continue a conversation.'}
              </p>
            </div>

            {activeTab === 'tickets' && !selectedTicket && (
              <button
                className="primary-button"
                onClick={() => setShowTicketForm(!showTicketForm)}
              >
                + Create ticket
              </button>
            )}
          </div>

          {error && <div className="dashboard-alert error-message">{error}</div>}
          {notice && <div className="dashboard-alert success-message">{notice}</div>}

          {loading ? (
            <div className="loading-card">Loading your dashboard...</div>
          ) : (
            <>
              {activeTab === 'overview' && (
                <>
                  <div className="stats-grid">
                    <StatCard label="Total books" value={books.length} icon="▤" />
                    <StatCard label="Open tickets" value={openCount} icon="✉" />
                    <StatCard
                      label="Pending royalties"
                      value={pendingRoyalty.toLocaleString('en-IN', {
                        maximumFractionDigits: 2,
                      })}
                      icon="₹"
                    />
                  </div>

                  <div className="content-card">
                    <div className="card-heading">
                      <div>
                        <h2>Recent support tickets</h2>
                        <p>Track your latest support requests.</p>
                      </div>
                      <button
                        className="text-button"
                        onClick={() => setActiveTab('tickets')}
                      >
                        View all
                      </button>
                    </div>

                    {tickets.length === 0 ? (
                      <EmptyState message="You haven't created any support tickets yet." />
                    ) : (
                      <TicketTable
                        tickets={tickets.slice(0, 5)}
                        onSelect={openTicket}
                      />
                    )}
                  </div>

                  <div className="content-card">
                    <div className="card-heading">
                      <div>
                        <h2>Your books</h2>
                        <p>A quick look at your books.</p>
                      </div>
                      <button
                        className="text-button"
                        onClick={() => setActiveTab('books')}
                      >
                        View all
                      </button>
                    </div>
                    {books.length === 0 ? (
                      <EmptyState message="No books are linked to your account yet." />
                    ) : (
                      <BookTable books={books.slice(0, 5)} />
                    )}
                  </div>
                </>
              )}

              {activeTab === 'books' && (
                <div className="content-card">
                  <div className="card-heading">
                    <div>
                      <h2>Book details</h2>
                      <p>{books.length} book(s) linked to your account.</p>
                    </div>
                  </div>
                  {books.length === 0 ? (
                    <EmptyState message="No books are linked to your account yet." />
                  ) : (
                    <BookTable books={books} detailed />
                  )}
                </div>
              )}

              {activeTab === 'tickets' && (
                <>
                  {showTicketForm && !selectedTicket && (
                    <div className="content-card ticket-form-card">
                      <div className="card-heading">
                        <div>
                          <h2>Create a support ticket</h2>
                          <p>Tell us how our support team can help.</p>
                        </div>
                      </div>

                      <form className="ticket-form" onSubmit={submitTicket}>
                        <label htmlFor="ticket-subject">Subject</label>
                        <input
                          id="ticket-subject"
                          value={ticketForm.subject}
                          onChange={(e) =>
                            setTicketForm({ ...ticketForm, subject: e.target.value })
                          }
                          placeholder="Briefly describe your issue"
                          required
                        />

                        <label htmlFor="ticket-category">Category</label>
                        <select
                          id="ticket-category"
                          value={ticketForm.category}
                          onChange={(e) =>
                            setTicketForm({ ...ticketForm, category: e.target.value })
                          }
                        >
                          <option>General</option>
                          <option>Book Publishing</option>
                          <option>Royalties</option>
                          <option>Payments</option>
                          <option>Technical Support</option>
                          <option>Other</option>
                        </select>

                        <label htmlFor="ticket-book">Related book (optional)</label>
                        <select
                          id="ticket-book"
                          value={ticketForm.book_id}
                          onChange={(e) =>
                            setTicketForm({ ...ticketForm, book_id: e.target.value })
                          }
                        >
                          <option value="">No specific book</option>
                          {books.map((book) => (
                            <option key={book.book_id} value={book.book_id}>
                              {book.title}
                            </option>
                          ))}
                        </select>

                        <label htmlFor="ticket-description">Description</label>
                        <textarea
                          id="ticket-description"
                          rows="5"
                          value={ticketForm.description}
                          onChange={(e) =>
                            setTicketForm({
                              ...ticketForm,
                              description: e.target.value,
                            })
                          }
                          placeholder="Explain your issue in detail..."
                          required
                        />

                        <div className="form-actions">
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() => setShowTicketForm(false)}
                          >
                            Cancel
                          </button>
                          <button
                            className="primary-button"
                            type="submit"
                            disabled={actionLoading}
                          >
                            {actionLoading ? 'Submitting...' : 'Submit ticket'}
                          </button>
                        </div>
                      </form>
                    </div>
                  )}

                  {selectedTicket ? (
                    <div className="content-card conversation-card">
                      <button
                        className="text-button back-button"
                        onClick={() => {
                          setSelectedTicket(null)
                          setReplies([])
                          setError('')
                          setNotice('')
                        }}
                      >
                        ← Back to tickets
                      </button>

                      <div className="conversation-heading">
                        <div>
                          <p className="eyebrow">
                            TICKET #{selectedTicket.ticket_id}
                          </p>
                          <h2>{selectedTicket.subject}</h2>
                          <p>{selectedTicket.description}</p>
                        </div>
                        <StatusBadge status={selectedTicket.status} />
                      </div>

                      <div className="reply-list">
                        {replies.length === 0 ? (
                          <EmptyState message="No replies yet. Send a message to start the conversation." />
                        ) : (
                          replies.map((reply) => (
                            <div
                              key={reply.reply_id}
                              className={`reply-bubble ${
                                reply.sender_role === 'author' ? 'author-reply' : ''
                              }`}
                            >
                              <div className="reply-meta">
                                <strong>
                                  {reply.sender_role === 'author'
                                    ? 'You'
                                    : 'BookLeaf Support'}
                                </strong>
                                <span>
                                  {reply.created_at
                                    ? new Date(reply.created_at).toLocaleString()
                                    : ''}
                                </span>
                              </div>
                              <p>{reply.message}</p>
                            </div>
                          ))
                        )}
                      </div>

                      <form className="reply-form" onSubmit={submitReply}>
                        <textarea
                          rows="3"
                          value={replyMessage}
                          onChange={(e) => setReplyMessage(e.target.value)}
                          placeholder="Write your reply..."
                          required
                        />
                        <button
                          className="primary-button"
                          type="submit"
                          disabled={actionLoading || !replyMessage.trim()}
                        >
                          {actionLoading ? 'Sending...' : 'Send reply'}
                        </button>
                      </form>
                    </div>
                  ) : !showTicketForm ? (
                    <div className="content-card">
                      <div className="card-heading">
                        <div>
                          <h2>All support tickets</h2>
                          <p>{tickets.length} ticket(s) found.</p>
                        </div>
                      </div>
                      {tickets.length === 0 ? (
                        <EmptyState message="You haven't created any support tickets yet." />
                      ) : (
                        <TicketTable tickets={tickets} onSelect={openTicket} />
                      )}
                    </div>
                  ) : null}
                </>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  )
}

function StatCard({ label, value, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  )
}

function StatusBadge({ status }) {
  const normalized = (status || 'Unknown').toLowerCase().replace(/\s+/g, '-')

  return <span className={`status-badge status-${normalized}`}>{status || 'Unknown'}</span>
}

function TicketTable({ tickets, onSelect }) {
  return (
    <div className="table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            <th>Ticket</th>
            <th>Subject</th>
            <th>Category</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr
              key={ticket.ticket_id}
              className="clickable-row"
              onClick={() => onSelect(ticket)}
            >
              <td>#{ticket.ticket_id}</td>
              <td className="table-title">{ticket.subject}</td>
              <td>{ticket.category}</td>
              <td>{ticket.priority}</td>
              <td><StatusBadge status={ticket.status} /></td>
              <td>
                {ticket.updated_at
                  ? new Date(ticket.updated_at).toLocaleDateString()
                  : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function BookTable({ books, detailed = false }) {
  return (
    <div className="table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            <th>Book title</th>
            <th>ISBN</th>
            <th>Status</th>
            {detailed && <th>Copies sold</th>}
            {detailed && <th>Royalty earned</th>}
            {detailed && <th>Royalty pending</th>}
          </tr>
        </thead>
        <tbody>
          {books.map((book) => (
            <tr key={book.book_id}>
              <td className="table-title">{book.title}</td>
              <td>{book.isbn || '—'}</td>
              <td><StatusBadge status={book.status} /></td>
              {detailed && <td>{book.total_copies_sold ?? 0}</td>}
              {detailed && <td>{book.total_royalty_earned ?? '—'}</td>}
              {detailed && <td>{book.royalty_pending ?? '—'}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function EmptyState({ message }) {
  return <div className="empty-state">{message}</div>
}

export default App
