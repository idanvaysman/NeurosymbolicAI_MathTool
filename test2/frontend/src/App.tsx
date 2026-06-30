import { FormEvent, useState } from 'react'

type Stats = {
  input_tokens: number
  output_tokens: number
  elapsed_time: number
}

type Solution = {
  result_text: string
  raw_result?: string
  latex?: string
  stats: Stats
}

type SolveResponse = {
  framework: Solution
  direct: Solution
}

const defaultPrompt = 'Integrate (x^3 * cos(x^2)) / (1 + sin(x^2)) with respect to x from 0 to sqrt(pi/2)'

function App() {
  const [prompt, setPrompt] = useState(defaultPrompt)
  const [frameworkResult, setFrameworkResult] = useState<Solution | null>(null)
  const [directResult, setDirectResult] = useState<Solution | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/api/solve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}))
        throw new Error(errorBody.detail ?? 'Request failed')
      }

      const payload: SolveResponse = await response.json()
      setFrameworkResult(payload.framework)
      setDirectResult(payload.direct)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1>Local Math Agent</h1>
        <p>FastAPI backend with SymPy self-healing logic and a TypeScript UI.</p>
      </header>

      <form onSubmit={handleSubmit} className="input-card">
        <label htmlFor="prompt">Enter a math prompt</label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          rows={4}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Running…' : 'Run Benchmarks'}
        </button>
      </form>

      {error ? <div className="error">{error}</div> : null}

      <div className="panels">
        <section className="panel">
          <h2>Agent Framework</h2>
          <p className="panel-subtitle">SymPy verified + 3x self-healing loop</p>
          {frameworkResult ? (
            <>
              <div className="result-box">{frameworkResult.result_text}</div>
              {frameworkResult.raw_result ? <pre>{frameworkResult.raw_result}</pre> : null}
              {frameworkResult.latex ? <pre>{frameworkResult.latex}</pre> : null}
              <div className="metrics">
                <div><strong>Input tokens</strong><span>{frameworkResult.stats.input_tokens}</span></div>
                <div><strong>Output tokens</strong><span>{frameworkResult.stats.output_tokens}</span></div>
                <div><strong>Elapsed</strong><span>{frameworkResult.stats.elapsed_time.toFixed(3)}s</span></div>
              </div>
            </>
          ) : (
            <p className="empty">Waiting for the first run.</p>
          )}
        </section>

        <section className="panel">
          <h2>Direct LLM</h2>
          <p className="panel-subtitle">Zero-shot answer</p>
          {directResult ? (
            <>
              <div className="result-box">{directResult.result_text}</div>
              <div className="metrics">
                <div><strong>Input tokens</strong><span>{directResult.stats.input_tokens}</span></div>
                <div><strong>Output tokens</strong><span>{directResult.stats.output_tokens}</span></div>
                <div><strong>Elapsed</strong><span>{directResult.stats.elapsed_time.toFixed(3)}s</span></div>
              </div>
            </>
          ) : (
            <p className="empty">Waiting for the first run.</p>
          )}
        </section>
      </div>
    </div>
  )
}

export default App
