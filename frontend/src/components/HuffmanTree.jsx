import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'

function TreeViz({ treeData }) {
    const svgRef = useRef(null)

    useEffect(() => {
        if (!treeData || !svgRef.current) return
        const el = svgRef.current
        d3.select(el).selectAll('*').remove()

        const margin = { top: 40, right: 30, bottom: 40, left: 30 }
        const nodeR = 28

        // Build D3 hierarchy
        const root = d3.hierarchy(treeData, d => d.children && d.children.length ? d.children : null)

        const treeLayout = d3.tree().nodeSize([90, 96])
        treeLayout(root)

        // Compute bounds
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
        root.each(n => {
            if (n.x < minX) minX = n.x
            if (n.x > maxX) maxX = n.x
            if (n.y < minY) minY = n.y
            if (n.y > maxY) maxY = n.y
        })
        const width = (maxX - minX) + margin.left + margin.right + nodeR * 2
        const height = (maxY - minY) + margin.top + margin.bottom + nodeR * 2
        const offsetX = -minX + margin.left + nodeR
        const offsetY = margin.top + nodeR

        const svg = d3.select(el)
            .attr('width', Math.max(width, 400))
            .attr('height', Math.max(height, 200))

        const g = svg.append('g').attr('transform', `translate(${offsetX},${offsetY})`)

        // Links
        g.selectAll('.link')
            .data(root.links())
            .enter().append('path')
            .attr('class', 'link')
            .attr('stroke', '#3b3b7a')
            .attr('d', d3.linkVertical().x(d => d.x).y(d => d.y))

        // Edge labels (0/1)
        g.selectAll('.edge-label')
            .data(root.links())
            .enter().append('text')
            .attr('x', d => (d.source.x + d.target.x) / 2)
            .attr('y', d => (d.source.y + d.target.y) / 2)
            .attr('text-anchor', 'middle')
            .attr('dy', -4)
            .attr('fill', '#a78bfa')
            .attr('font-size', '11px')
            .attr('font-family', 'JetBrains Mono, monospace')
            .text(d => d.target.data.edge_label || '')

        // Nodes
        const node = g.selectAll('.node')
            .data(root.descendants())
            .enter().append('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${d.x},${d.y})`)

        node.append('circle')
            .attr('r', nodeR)
            .attr('fill', d => {
                if (d.data.label === 'NYT') return '#1e3a5f'
                if (d.data.char) return 'linear-gradient(135deg,#4c1d95,#1d4ed8)'
                return '#1a1a40'
            })
            .attr('stroke', d => {
                if (d.data.label === 'NYT') return '#38bdf8'
                if (d.data.char) return '#7c3aed'
                return '#3b3b7a'
            })
            .style('filter', d => d.data.char ? 'drop-shadow(0 0 8px rgba(124,58,237,0.5))' : 'none')

        // Character label
        node.filter(d => d.data.char || d.data.label === 'NYT')
            .append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', -6)
            .attr('fill', d => d.data.label === 'NYT' ? '#38bdf8' : '#a78bfa')
            .attr('font-size', '11px')
            .attr('font-family', 'JetBrains Mono, monospace')
            .attr('font-weight', '600')
            .text(d => {
                if (d.data.label === 'NYT') return 'NYT'
                if (d.data.char === ' ') return '⎵'
                return `'${d.data.char}'`
            })

        // Frequency label
        node.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', d => (d.data.char || d.data.label === 'NYT') ? 8 : 5)
            .attr('fill', '#e2e8f0')
            .attr('font-size', '12px')
            .attr('font-family', 'JetBrains Mono, monospace')
            .text(d => d.data.freq)

    }, [treeData])

    return (
        <div className="tree-svg-wrap">
            <svg ref={svgRef} />
        </div>
    )
}

export default function HuffmanTree({ treeData, snapshots }) {
    const [snapshotIdx, setSnapshotIdx] = useState(null)

    const hasSnapshots = snapshots && snapshots.length > 1
    const displayTree = hasSnapshots && snapshotIdx !== null ? snapshots[snapshotIdx] : treeData

    return (
        <div>
            {hasSnapshots && (
                <div className="snapshot-nav">
                    <button
                        disabled={snapshotIdx === null || snapshotIdx === 0}
                        onClick={() => setSnapshotIdx(i => Math.max(0, (i ?? snapshots.length - 1) - 1))}
                    >← Prev</button>
                    <span>
                        {snapshotIdx === null
                            ? `Final tree (after all ${snapshots.length} chars)`
                            : `After char ${snapshotIdx + 1} of ${snapshots.length}`}
                    </span>
                    <button
                        disabled={snapshotIdx !== null && snapshotIdx === snapshots.length - 1}
                        onClick={() => setSnapshotIdx(i => (i === null ? 0 : Math.min(snapshots.length - 1, i + 1)))}
                    >Next →</button>
                    <button
                        onClick={() => setSnapshotIdx(null)}
                        style={{ marginLeft: 'auto', color: 'var(--accent2)' }}
                    >Final ⟩⟩</button>
                </div>
            )}
            <TreeViz treeData={displayTree} />
            <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: 8 }}>
                🟣 Leaf nodes (characters) · ⬡ Internal nodes (frequencies) · Edge labels: 0 = left, 1 = right
            </p>
        </div>
    )
}
