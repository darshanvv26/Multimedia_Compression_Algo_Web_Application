import { useState } from 'react'

export default function StepFlow({ steps }) {
    const [open, setOpen] = useState({})

    const toggle = (i) => setOpen(o => ({ ...o, [i]: !o[i] }))

    return (
        <div style={{ marginTop: 4 }}>
            {steps.map((step, i) => {
                const isOpen = open[i] !== false // default open
                return (
                    <div className="step-card" key={i} style={{ animationDelay: `${i * 0.07}s` }}>
                        <div className="step-header" onClick={() => toggle(i)}>
                            <div className="step-num">{i + 1}</div>
                            <div className="step-title">{step.title}</div>
                            <div className="step-toggle">{isOpen ? '▲' : '▼'}</div>
                        </div>
                        {isOpen && (
                            <div className="step-body">
                                {step.description && (
                                    <div className="step-desc">{step.description}</div>
                                )}
                                {step.table && (
                                    <div className="step-table-wrap">
                                        <table>
                                            <thead>
                                                <tr>{step.table.headers.map((h, j) => <th key={j}>{h}</th>)}</tr>
                                            </thead>
                                            <tbody>
                                                {step.table.rows.map((row, j) => (
                                                    <tr key={j}>{row.map((cell, k) => <td key={k}>{cell}</td>)}</tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                                {step.summary && (
                                    <div className="step-summary">{step.summary}</div>
                                )}
                            </div>
                        )}
                    </div>
                )
            })}
        </div>
    )
}
