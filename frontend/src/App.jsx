import { useState } from 'react'
import axios from 'axios'
import StepFlow from './components/StepFlow'
import HuffmanTree from './components/HuffmanTree'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const ALGORITHMS = [
    { id: 'static_huffman', icon: '🌳', name: 'Static Huffman', tag: 'Entropy · Tree-based' },
    { id: 'dynamic_huffman', icon: '🔄', name: 'Dynamic Huffman', tag: 'Adaptive · NYT Node' },
    { id: 'arithmetic', icon: '📐', name: 'Arithmetic', tag: 'Interval · Float output' },
    { id: 'lzw', icon: '📖', name: 'LZW', tag: 'Dictionary · Greedy match' },
]

export default function App() {
    const [algo, setAlgo] = useState('static_huffman')
    const [text, setText] = useState('hello world')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleCompress = async () => {
        setLoading(true); setError(null); setResult(null)
        try {
            const { data } = await axios.post(`${API}/compress`, { algorithm: algo, text })
            setResult(data)
        } catch (e) {
            setError(e.response?.data?.detail || 'Something went wrong.')
        } finally {
            setLoading(false)
        }
    }

    const hasTree = result && result.tree

    return (
        <div className="app">
            <header className="header">
                <div className="header-logo">🗜️</div>
                <div>
                    <h1>Compression <span>Explorer</span></h1>
                    <p>Visualise how compression algorithms work — step by step</p>
                </div>
            </header>

            <div className="main">
                {/* Sidebar */}
                <nav className="sidebar">
                    <div className="sidebar-label">Algorithm</div>
                    {ALGORITHMS.map(a => (
                        <button
                            key={a.id}
                            className={`algo-btn ${algo === a.id ? 'active' : ''}`}
                            onClick={() => { setAlgo(a.id); setResult(null); setError(null) }}
                        >
                            <span className="icon">{a.icon}</span>
                            <div className="algo-info">
                                <div className="algo-name">{a.name}</div>
                                <div className="algo-tag">{a.tag}</div>
                            </div>
                        </button>
                    ))}
                </nav>

                {/* Main content */}
                <div className="content">
                    {/* Input */}
                    <div className="panel">
                        <div className="panel-title">Input Text</div>
                        <textarea
                            value={text}
                            onChange={e => setText(e.target.value)}
                            placeholder="Type or paste text to compress…"
                            rows={4}
                        />
                        <button className="btn-compress" onClick={handleCompress} disabled={loading || !text.trim()}>
                            {loading ? <span className="spinner" /> : '⚡'}
                            {loading ? 'Compressing…' : `Run ${ALGORITHMS.find(a => a.id === algo)?.name}`}
                        </button>
                    </div>

                    {error && <div className="error-box">⚠️ {error}</div>}

                    {result && (
                        <>
                            {/* Stats */}
                            <div className="stats-bar">
                                <div className="stat-card">
                                    <div className="label">Original</div>
                                    <div className="value blue">{result.original_bits} <span style={{ fontSize: '0.7rem', color: 'var(--muted)' }}>bits</span></div>
                                </div>
                                <div className="stat-card">
                                    <div className="label">Compressed</div>
                                    <div className="value purple">{result.compressed_bits} <span style={{ fontSize: '0.7rem', color: 'var(--muted)' }}>bits</span></div>
                                </div>
                                <div className="stat-card">
                                    <div className="label">Ratio</div>
                                    <div className="value yellow">{result.compression_ratio}×</div>
                                </div>
                                <div className="stat-card">
                                    <div className="label">Space Saved</div>
                                    <div className="value green">{result.space_saved_percent}%</div>
                                </div>
                            </div>

                            {/* Compressed output */}
                            <div className="panel">
                                <div className="panel-title">Compressed Output</div>
                                <div className="compressed-output">{result.compressed}</div>
                            </div>

                            {/* Huffman Tree */}
                            {hasTree && (
                                <div className="panel tree-panel">
                                    <div className="panel-title">
                                        {result.algorithm === 'Dynamic Huffman' ? 'Final Adaptive Huffman Tree' : 'Huffman Tree'}
                                    </div>
                                    <HuffmanTree
                                        treeData={result.tree}
                                        snapshots={result.tree_snapshots}
                                    />
                                </div>
                            )}

                            {/* Step-by-step flow */}
                            {result.steps && result.steps.length > 0 && (
                                <div className="panel">
                                    <div className="panel-title">Mathematical Flow — Step by Step</div>
                                    <StepFlow steps={result.steps} />
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
