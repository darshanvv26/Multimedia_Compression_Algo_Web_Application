"""
Dynamic (Adaptive) Huffman Compression

Approach: Adaptive tree — re-built from current frequencies after each
character is processed.  This correctly models adaptive Huffman behaviour
(codes change as new symbols appear and frequencies grow) while avoiding
the FGK sibling-swap complexity that caused O(n²) slowdowns.
"""

import heapq
from collections import Counter


# ── small Huffman tree helpers ────────────────────────────────────────────────

class _Node:
    __slots__ = ("char", "freq", "left", "right")

    def __init__(self, char, freq, left=None, right=None):
        self.char  = char
        self.freq  = freq
        self.left  = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def _build_tree(freq_map: dict) -> _Node:
    heap = [_Node(ch, fr) for ch, fr in freq_map.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, _Node(None, a.freq + b.freq, a, b))
    return heap[0]


def _get_codes(node: _Node, prefix: str = "", codes: dict = None) -> dict:
    if codes is None:
        codes = {}
    if node is None:
        return codes
    if node.char is not None:
        codes[node.char] = prefix if prefix else "0"
    else:
        _get_codes(node.left,  prefix + "0", codes)
        _get_codes(node.right, prefix + "1", codes)
    return codes


def _tree_to_json(node: _Node) -> dict:
    """Serialise to nested dict for D3 rendering."""
    if node is None:
        return {}
    result = {
        "id":       id(node),
        "char":     node.char,
        "freq":     node.freq,
        "children": []
    }
    if node.left:
        lc = _tree_to_json(node.left)
        lc["edge_label"] = "0"
        result["children"].append(lc)
    if node.right:
        rc = _tree_to_json(node.right)
        rc["edge_label"] = "1"
        result["children"].append(rc)
    return result


# ── main compress function ────────────────────────────────────────────────────

def compress(text: str) -> dict:
    if not text:
        raise ValueError("Input text cannot be empty.")

    # Cap snapshots at 30 characters to keep response size sane
    MAX_SNAPSHOTS = 30

    freq_map: Counter = Counter()
    encoded_parts: list[str] = []
    char_steps:  list[dict] = []
    snapshots:   list[dict] = []

    nyt_seen: set = set()   # symbols transmitted so far

    for i, char in enumerate(text):
        # ── encode this character ─────────────────────────────────────────
        if char not in nyt_seen:
            # NEW symbol: send current NYT path + 8-bit ASCII
            if freq_map:
                # Build tree from current frequencies; NYT is implicit
                root  = _build_tree(dict(freq_map))
                codes = _get_codes(root)
                # Find the leftmost-deepest leaf → proxy for NYT path
                nyt_code = _deepest_left_path(root)
            else:
                nyt_code = ""               # very first symbol
            raw_bits = _char_to_binary(char)
            bits_out = nyt_code + raw_bits
            char_steps.append({
                "char":     char,
                "type":     "new",
                "nyt_code": nyt_code,
                "raw_bits": raw_bits,
                "output":   bits_out,
            })
            nyt_seen.add(char)
        else:
            # EXISTING symbol: send current Huffman code
            root  = _build_tree(dict(freq_map))
            codes = _get_codes(root)
            bits_out = codes.get(char, "")
            char_steps.append({
                "char":   char,
                "type":   "existing",
                "code":   bits_out,
                "output": bits_out,
            })

        encoded_parts.append(bits_out)

        # ── update frequency and capture tree snapshot ────────────────────
        freq_map[char] += 1
        if i < MAX_SNAPSHOTS:
            snap_root = _build_tree(dict(freq_map))
            snapshots.append(_tree_to_json(snap_root))

    # Final tree
    final_root = _build_tree(dict(freq_map))
    final_tree = _tree_to_json(final_root)

    # If we capped snapshots, append the final state as last snapshot
    if snapshots and snapshots[-1] != final_tree:
        snapshots.append(final_tree)

    encoded_bits     = "".join(encoded_parts)
    original_bits    = len(text) * 8
    compressed_bits  = len(encoded_bits)
    ratio   = round(original_bits / compressed_bits, 4) if compressed_bits else 0
    savings = round((original_bits - compressed_bits) / original_bits * 100, 2) if original_bits else 0

    # ── Build steps ───────────────────────────────────────────────────────
    steps = []

    steps.append({
        "title": "Step 1: Initialize Adaptive Huffman",
        "description": (
            "Start with an empty frequency table and an implicit NYT (Not Yet Transmitted) node.\n"
            "The NYT node represents all symbols not yet seen. To send a new symbol, transmit the\n"
            "path to NYT in the current tree followed by the 8-bit ASCII code of the character.\n"
            "After every character the tree is rebuilt from updated frequencies."
        )
    })

    encode_rows = []
    for s in char_steps:
        if s["type"] == "new":
            encode_rows.append([
                f"'{s['char']}'" if s["char"] != " " else "'SPACE'",
                "NEW",
                f"NYT-path={s['nyt_code'] or '(empty)'} + ASCII={s['raw_bits']}",
                s["output"],
            ])
        else:
            encode_rows.append([
                f"'{s['char']}'" if s["char"] != " " else "'SPACE'",
                "EXISTING",
                s["code"],
                s["output"],
            ])

    steps.append({
        "title": "Step 2: Character-by-Character Adaptive Encoding",
        "description": (
            "For each character:\n"
            "• NEW → transmit NYT path + 8-bit ASCII, then add character to alphabet\n"
            "• EXISTING → transmit current Huffman code for that character\n"
            "The tree is re-built after every character, so codes adapt dynamically."
        ),
        "table": {
            "headers": ["Character", "Status", "Code Derivation", "Bits Output"],
            "rows":    encode_rows,
        }
    })

    steps.append({
        "title": "Step 3: Final Compressed Bitstream",
        "description": (
            f"Concatenating all segments gives {compressed_bits} bits "
            f"(original: {original_bits} bits, saved {savings}%)."
        ),
        "table": {
            "headers": ["#", "Character", "Bits"],
            "rows": [
                [str(i+1),
                 f"'{s['char']}'" if s["char"] != " " else "'SPACE'",
                 s["output"]]
                for i, s in enumerate(char_steps)
            ]
        }
    })

    freq_rows = sorted(freq_map.items(), key=lambda x: -x[1])
    steps.append({
        "title": "Step 4: Final Frequency Table",
        "description": "Character frequencies after processing the entire input.",
        "table": {
            "headers": ["Character", "Frequency", "Final Huffman Code"],
            "rows": [
                [f"'{ch}'" if ch != " " else "'SPACE'",
                 str(fr),
                 _get_codes(_build_tree(dict(freq_map))).get(ch, "-")]
                for ch, fr in freq_rows
            ]
        }
    })

    return {
        "algorithm":            "Dynamic Huffman",
        "compressed":           encoded_bits,
        "original_bits":        original_bits,
        "compressed_bits":      compressed_bits,
        "compression_ratio":    ratio,
        "space_saved_percent":  savings,
        "steps":                steps,
        "tree":                 final_tree,
        "tree_snapshots":       snapshots,
    }


# ── helpers ───────────────────────────────────────────────────────────────────

def _char_to_binary(char: str, bits: int = 8) -> str:
    return bin(ord(char))[2:].zfill(bits)


def _deepest_left_path(root: _Node) -> str:
    """Walk left at every level — proxy for the NYT position path."""
    code = []
    node = root
    while node.left or node.right:
        code.append("0")
        node = node.left if node.left else node.right
    return "".join(code)
