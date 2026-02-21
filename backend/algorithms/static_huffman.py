import heapq
from collections import Counter
from typing import Any


class HuffmanNode:
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def _build_tree(frequencies: dict) -> HuffmanNode:
    heap = [HuffmanNode(ch, fr) for ch, fr in frequencies.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = HuffmanNode(None, n1.freq + n2.freq, n1, n2)
        heapq.heappush(heap, merged)
    return heap[0]


def _generate_codes(node: HuffmanNode, prefix: str = "", codes: dict = None) -> dict:
    if codes is None:
        codes = {}
    if node is None:
        return codes
    if node.char is not None:
        codes[node.char] = prefix if prefix else "0"
    else:
        _generate_codes(node.left, prefix + "0", codes)
        _generate_codes(node.right, prefix + "1", codes)
    return codes


def _tree_to_json(node: HuffmanNode, node_id: list = None) -> dict:
    """Convert tree to a list of nodes and edges for D3 visualization."""
    if node_id is None:
        node_id = [0]
    my_id = node_id[0]
    node_id[0] += 1

    result = {
        "id": my_id,
        "char": node.char if node.char is not None else None,
        "freq": node.freq,
        "children": []
    }

    if node.left:
        left_child = _tree_to_json(node.left, node_id)
        left_child["edge_label"] = "0"
        result["children"].append(left_child)
    if node.right:
        right_child = _tree_to_json(node.right, node_id)
        right_child["edge_label"] = "1"
        result["children"].append(right_child)

    return result


def compress(text: str) -> dict:
    if not text:
        raise ValueError("Input text cannot be empty.")

    # Step 1: Frequency analysis
    frequencies = dict(Counter(text))
    steps = []
    steps.append({
        "title": "Step 1: Character Frequency Analysis",
        "description": "Count occurrences of each character in the input.",
        "table": {
            "headers": ["Character", "Frequency"],
            "rows": [[f"'{ch}'" if ch != ' ' else "'SPACE'", str(fr)]
                     for ch, fr in sorted(frequencies.items(), key=lambda x: -x[1])]
        }
    })

    # Step 2: Build priority queue
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1])
    steps.append({
        "title": "Step 2: Build Min-Heap (Priority Queue)",
        "description": "Create a leaf node for each character. Insert all nodes into a min-heap ordered by frequency.",
        "table": {
            "headers": ["Priority", "Character", "Frequency"],
            "rows": [[str(i+1), f"'{ch}'" if ch != ' ' else "'SPACE'", str(fr)]
                     for i, (ch, fr) in enumerate(sorted_freq)]
        }
    })

    # Step 3: Merge nodes - show merge sequence
    merge_heap = [HuffmanNode(ch, fr) for ch, fr in sorted_freq]
    heapq.heapify(merge_heap)
    merge_steps = []
    step_num = 1
    temp_heap = [HuffmanNode(ch, fr) for ch, fr in sorted_freq]
    heapq.heapify(temp_heap)
    while len(temp_heap) > 1:
        n1 = heapq.heappop(temp_heap)
        n2 = heapq.heappop(temp_heap)
        label1 = f"'{n1.char}'" if n1.char and n1.char != ' ' else ("'SPACE'" if n1.char == ' ' else f"[internal:{n1.freq}]")
        label2 = f"'{n2.char}'" if n2.char and n2.char != ' ' else ("'SPACE'" if n2.char == ' ' else f"[internal:{n2.freq}]")
        merged = HuffmanNode(None, n1.freq + n2.freq, n1, n2)
        heapq.heappush(temp_heap, merged)
        merge_steps.append([str(step_num), label1, str(n1.freq), label2, str(n2.freq), str(merged.freq)])
        step_num += 1

    steps.append({
        "title": "Step 3: Merge Nodes to Build Huffman Tree",
        "description": "Repeatedly extract the two lowest-frequency nodes, merge them into an internal node with combined frequency, and re-insert.",
        "table": {
            "headers": ["Merge #", "Node A", "Freq A", "Node B", "Freq B", "New Node Freq"],
            "rows": merge_steps
        }
    })

    # Step 4: Generate codes
    root = _build_tree(frequencies)
    codes = _generate_codes(root)

    steps.append({
        "title": "Step 4: Generate Huffman Codes (DFS Traversal)",
        "description": "Traverse the tree: go left → append '0', go right → append '1'. Leaf node path = code for that character.",
        "table": {
            "headers": ["Character", "Frequency", "Huffman Code", "Code Length"],
            "rows": [[f"'{ch}'" if ch != ' ' else "'SPACE'", str(frequencies[ch]), codes[ch], str(len(codes[ch]))]
                     for ch in sorted(codes.keys())]
        }
    })

    # Step 5: Encode
    encoded = "".join(codes[ch] for ch in text)
    original_bits = len(text) * 8
    compressed_bits = len(encoded)
    ratio = original_bits / compressed_bits if compressed_bits > 0 else 0
    savings = ((original_bits - compressed_bits) / original_bits * 100) if original_bits > 0 else 0

    steps.append({
        "title": "Step 5: Encode Input String",
        "description": "Replace each character with its Huffman code to produce the compressed bitstream.",
        "table": {
            "headers": ["Character", "Huffman Code"],
            "rows": [[f"'{ch}'" if ch != ' ' else "'SPACE'", codes[ch]] for ch in text]
        },
        "summary": f"Original: {original_bits} bits | Compressed: {compressed_bits} bits | Ratio: {ratio:.2f}x | Space saved: {savings:.1f}%"
    })

    tree_json = _tree_to_json(root)

    return {
        "algorithm": "Static Huffman",
        "compressed": encoded,
        "original_bits": original_bits,
        "compressed_bits": compressed_bits,
        "compression_ratio": round(ratio, 4),
        "space_saved_percent": round(savings, 2),
        "codes": {ch: codes[ch] for ch in sorted(codes.keys())},
        "steps": steps,
        "tree": tree_json
    }
