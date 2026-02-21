from collections import Counter


def compress(text: str) -> dict:
    if not text:
        raise ValueError("Input text cannot be empty.")

    # Step 1: Build probability model from input frequencies
    freq = Counter(text)
    total = len(text)
    steps = []

    # Assign probability ranges
    sorted_chars = sorted(freq.keys())
    low_val = 0.0
    prob_model = {}
    prob_table_rows = []
    for ch in sorted_chars:
        prob = freq[ch] / total
        high_val = low_val + prob
        prob_model[ch] = {"prob": prob, "low": low_val, "high": high_val}
        prob_table_rows.append([
            f"'{ch}'" if ch != ' ' else "'SPACE'",
            str(freq[ch]),
            f"{prob:.4f}",
            f"[{low_val:.4f}, {high_val:.4f})"
        ])
        low_val = high_val

    steps.append({
        "title": "Step 1: Build Probability Model",
        "description": "Calculate each character's probability and assign a non-overlapping sub-interval of [0, 1).",
        "table": {
            "headers": ["Character", "Count", "Probability", "Interval [low, high)"],
            "rows": prob_table_rows
        }
    })

    # Step 2: Encode — interval narrowing
    low = 0.0
    high = 1.0
    interval_rows = []
    for i, symbol in enumerate(text):
        current_range = high - low
        new_low = low + current_range * prob_model[symbol]["low"]
        new_high = low + current_range * prob_model[symbol]["high"]
        interval_rows.append([
            str(i + 1),
            f"'{symbol}'" if symbol != ' ' else "'SPACE'",
            f"[{prob_model[symbol]['low']:.4f}, {prob_model[symbol]['high']:.4f})",
            f"[{low:.6f}, {high:.6f})",
            f"[{new_low:.6f}, {new_high:.6f})"
        ])
        low, high = new_low, new_high

    steps.append({
        "title": "Step 2: Iterative Interval Narrowing (Encoding)",
        "description": (
            "For each symbol, narrow the current interval [low, high) using the formula:\n"
            "  new_low  = low + (high − low) × symbol_low\n"
            "  new_high = low + (high − low) × symbol_high"
        ),
        "table": {
            "headers": ["#", "Symbol", "Symbol Range", "Current [low, high)", "New [low, high)"],
            "rows": interval_rows
        }
    })

    # Step 3: Final encoded value
    encoded_value = (low + high) / 2

    steps.append({
        "title": "Step 3: Select Final Encoded Value",
        "description": (
            f"The final interval is [{low:.8f}, {high:.8f}). "
            f"Pick the midpoint as the encoded value: ({low:.8f} + {high:.8f}) / 2 = {encoded_value:.8f}"
        )
    })

    # Step 4: Decode walkthrough
    decode_rows = []
    dlw, dhigh = 0.0, 1.0
    for i in range(len(text)):
        current_range = dhigh - dlw
        for sym, data in prob_model.items():
            sym_low = dlw + current_range * data["low"]
            sym_high = dlw + current_range * data["high"]
            if sym_low <= encoded_value < sym_high:
                decode_rows.append([str(i+1), f"'{sym}'" if sym != ' ' else "'SPACE'",
                                    f"{sym_low:.6f}", f"{sym_high:.6f}"])
                dlw, dhigh = sym_low, sym_high
                break

    steps.append({
        "title": "Step 4: Decode Verification",
        "description": "Starting from the encoded float, repeatedly find which symbol's interval contains the value, output the symbol, and narrow the interval.",
        "table": {
            "headers": ["#", "Decoded Symbol", "Interval Low", "Interval High"],
            "rows": decode_rows
        }
    })

    original_bits = len(text) * 8
    # Arithmetic encoding output is a single float; approximate bit count as mantissa bits needed
    import math
    compressed_bits = max(1, math.ceil(-math.log2(high - low))) if (high - low) > 0 else 64

    return {
        "algorithm": "Arithmetic",
        "compressed": str(round(encoded_value, 10)),
        "encoded_value": encoded_value,
        "final_low": low,
        "final_high": high,
        "original_bits": original_bits,
        "compressed_bits": compressed_bits,
        "compression_ratio": round(original_bits / compressed_bits, 4) if compressed_bits else 0,
        "space_saved_percent": round((1 - compressed_bits / original_bits) * 100, 2) if original_bits else 0,
        "prob_model": {k: {"prob": round(v["prob"], 6), "low": round(v["low"], 6), "high": round(v["high"], 6)}
                       for k, v in prob_model.items()},
        "steps": steps,
        "tree": None
    }
