def compress(text: str) -> dict:
    if not text:
        raise ValueError("Input text cannot be empty.")

    steps = []

    # Step 1: Initialize dictionary
    dictionary = {chr(i): i for i in range(256)}
    next_code = 256
    dict_init_rows = [[str(ord(ch)), f"'{ch}'" if ch != ' ' else "'SPACE'"] for ch in text[:10]]
    steps.append({
        "title": "Step 1: Initialize LZW Dictionary",
        "description": "Pre-populate the dictionary with all 256 single-character entries (ASCII). Each character maps to its ASCII code.",
        "table": {
            "headers": ["Code", "Symbol"],
            "rows": [[str(i), f"'{chr(i)}'" if chr(i) != ' ' else "'SPACE'"]
                     for i in range(min(256, 32)) if chr(i).isprintable()] + [["...", "..."]]
        }
    })

    # Step 2: Encode with dictionary growth tracking
    dictionary = {chr(i): i for i in range(256)}
    next_code = 256
    w = ""
    output_codes = []
    encode_rows = []
    dict_growth_rows = []

    for i, c in enumerate(text):
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            code = dictionary[w]
            output_codes.append(code)
            sym_display = f"'{w}'" if w != ' ' else "'SPACE'"
            encode_rows.append([str(len(encode_rows)+1), sym_display, str(code), f"'{c}'", f"'{wc}'", str(next_code)])
            dict_growth_rows.append([str(next_code), f"'{wc}'"])
            dictionary[wc] = next_code
            next_code += 1
            w = c

    # Don't forget w
    if w:
        code = dictionary[w]
        output_codes.append(code)
        sym_display = f"'{w}'" if w != ' ' else "'SPACE'"
        encode_rows.append([str(len(encode_rows)+1), sym_display, str(code), "-", "-", "-"])

    steps.append({
        "title": "Step 2: Encoding — Greedy Dictionary Matching",
        "description": (
            "Read characters one by one. Keep extending the current string W while W+C is in the dictionary. "
            "When W+C is not found: output code for W, add W+C to dictionary with new code, set W = C."
        ),
        "table": {
            "headers": ["Step", "W (current string)", "Code(W)", "Next char C", "W+C (new entry)", "Assigned Code"],
            "rows": encode_rows
        }
    })

    steps.append({
        "title": "Step 3: Dictionary Growth",
        "description": "New entries added to the dictionary during encoding. The receiver can reconstruct this same dictionary during decoding.",
        "table": {
            "headers": ["Code", "String"],
            "rows": dict_growth_rows if dict_growth_rows else [["(none)", "Input too short to grow dictionary"]]
        }
    })

    # Step 4: Final output code sequence
    steps.append({
        "title": "Step 4: Output Code Sequence",
        "description": "The compressed representation is this sequence of integer codes. Each code refers to a dictionary entry.",
        "table": {
            "headers": ["Position", "Code"],
            "rows": [[str(i+1), str(c)] for i, c in enumerate(output_codes)]
        }
    })

    # Compression stats
    original_bits = len(text) * 8
    # Assume 12-bit codes (standard LZW)
    compressed_bits = len(output_codes) * 12
    ratio = original_bits / compressed_bits if compressed_bits > 0 else 0
    savings = ((original_bits - compressed_bits) / original_bits * 100) if original_bits > 0 else 0

    return {
        "algorithm": "LZW",
        "compressed": " ".join(str(c) for c in output_codes),
        "output_codes": output_codes,
        "original_bits": original_bits,
        "compressed_bits": compressed_bits,
        "compression_ratio": round(ratio, 4),
        "space_saved_percent": round(savings, 2),
        "steps": steps,
        "tree": None
    }
