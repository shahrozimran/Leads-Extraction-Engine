import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [country, setCountry] = useState('')
  const [maxResults, setMaxResults] = useState(50)
  const [sheetName, setSheetName] = useState('My Leads')
  const [isScraping, setIsScraping] = useState(false)
  const [logs, setLogs] = useState([])
  const [leads, setLeads] = useState([])
  
  const consoleRef = useRef(null)

  // Auto-scroll the console
  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight
    }
  }, [logs])

  const startScraping = (e) => {
    e.preventDefault()
    if (!query || !sheetName) return

    setIsScraping(true)
    setLogs([])
    setLeads([])

    // SSE connection
    const eventSource = new EventSource(`http://127.0.0.1:8000/api/scrape/stream?query=${encodeURIComponent(query)}&country=${encodeURIComponent(country)}&max_results=${maxResults}&sheet_name=${encodeURIComponent(sheetName)}`)

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'log') {
        setLogs(prev => [...prev, data.message])
      } else if (data.type === 'lead') {
        setLeads(prev => [...prev, data.data])
      } else if (data.type === 'error') {
        setLogs(prev => [...prev, `[ERROR] ${data.message}`])
        eventSource.close()
        setIsScraping(false)
      } else if (data.type === 'complete') {
        setLogs(prev => [...prev, "[✓] Process fully completed."])
        eventSource.close()
        setIsScraping(false)
      }
    }

    eventSource.onerror = (err) => {
      console.error("SSE Error:", err)
      setLogs(prev => [...prev, "[!] Connection dropped or errored out."])
      eventSource.close()
      setIsScraping(false)
    }
  }

  return (
    <div className="app-container">
      <div className="hero-section">
        <h1 className="gradient-text">Lead Extraction Engine</h1>
        <p className="subtitle">High-velocity, heuristic-filtered B2B scaling.</p>
      </div>

      <div className="dashboard">
        {/* Configuration Panel */}
        <div className="panel config-panel">
          <h2>Configuration</h2>
          <form onSubmit={startScraping}>
            <div className="form-row">
              <div className="form-group" style={{ flex: 2 }}>
                <label>Target Query</label>
                <input 
                  type="text" 
                  placeholder="e.g. tech companies hiring..." 
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  disabled={isScraping}
                />
              </div>
              
              <div className="form-group" style={{ flex: 1 }}>
                <label>Target Location</label>
                <input 
                  type="text"
                  placeholder="e.g. UK, Brazil, or leave empty"
                  value={country}
                  onChange={e => setCountry(e.target.value)}
                  disabled={isScraping}
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Max Leads</label>
                <input 
                  type="number" 
                  value={maxResults}
                  onChange={e => setMaxResults(e.target.value)}
                  disabled={isScraping}
                  min="1"
                  max="100"
                />
              </div>
              <div className="form-group">
                <label>Target Google Sheet</label>
                <input 
                  type="text" 
                  value={sheetName}
                  onChange={e => setSheetName(e.target.value)}
                  disabled={isScraping}
                />
              </div>
            </div>

            <button 
              className={`primary-btn ${isScraping ? 'scanning' : ''}`}
              type="submit" 
              disabled={isScraping}
            >
              {isScraping ? 'Extracting & Exporting...' : 'Initiate Extraction'}
            </button>
          </form>
        </div>

        {/* Live Console Output */}
        <div className="panel console-panel">
          <div className="console-header">
            <span className="dot red"></span>
            <span className="dot yellow"></span>
            <span className="dot green"></span>
            <span className="title">Extraction Flow</span>
          </div>
          <div className="console-monitor" ref={consoleRef}>
            {logs.length === 0 && !isScraping && (
              <div className="dim-text">Waiting for input...</div>
            )}
            {logs.map((log, index) => (
              <div key={index} className="log-line">
                <span className="log-arrow">{'>'}</span> {log}
              </div>
            ))}
            {isScraping && <div className="blinking-cursor">_</div>}
          </div>
        </div>
      </div>

      {/* Results Table */}
      {leads.length > 0 && (
        <div className="results-panel">
          <div className="results-header">
            <h2>Captured Leads <span className="badge">{leads.length}</span></h2>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Target URL</th>
                  <th>Email</th>
                  <th>Page Title</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead, i) => (
                  <tr key={i}>
                    <td className="url-cell"><a href={lead.url} target="_blank" rel="noreferrer">{lead.url}</a></td>
                    <td className="email-cell">{lead.email || '-'}</td>
                    <td className="title-cell">{lead.title}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
