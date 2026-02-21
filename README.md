# 🗜️ Compression Visualizer

A full-stack web application that demonstrates four classic data compression algorithms with step-by-step visualizations and interactive Huffman tree rendering.

---

## 🐳 Docker

**Image Repository:** [Docker Hub – `darshanvv26/compression-backend`](https://hub.docker.com/repository/docker/darshanvv26/compression-backend/)

**Image Repository:** [Docker Hub – `darshanvv26/compression-frontend`](https://hub.docker.com/repository/docker/darshanvv26/compression-frontend/)

> Pull and run the full stack with Docker Compose:

```bash
# Clone the repository
git clone https://github.com/darshanmakwana412/compression.git
cd compression

# Pull and start all services
docker compose up --build
```

| Service  | URL                    |
|----------|------------------------|
| Frontend | http://localhost:3000  |
| Backend  | http://localhost:8000  |

---

## 📁 Project Structure

```
compression/
│
├── 📓 Arithmetic_Compression.ipynb          # Jupyter notebook – Arithmetic coding exploration
├── 📓 Dynamic_Huffman_Compression.ipynb     # Jupyter notebook – Dynamic Huffman exploration
├── 📓 LZW_Compression.ipynb                 # Jupyter notebook – LZW coding exploration
├── 📓 Static_Huffman_Compression.ipynb      # Jupyter notebook – Static Huffman exploration
│
├── docker-compose.yml                       # Orchestrates backend + frontend containers
│
├── backend/
│   ├── Dockerfile                           # Backend container definition (Python/FastAPI)
│   ├── main.py                              # FastAPI app – API routes for all algorithms
│   ├── requirements.txt                     # Python dependencies
│   └── algorithms/
│       ├── static_huffman.py                # Static Huffman encoding implementation
│       ├── dynamic_huffman.py               # Dynamic (adaptive) Huffman encoding
│       ├── arithmetic.py                    # Arithmetic coding implementation
│       └── lzw.py                           # Lempel–Ziv–Welch (LZW) implementation
│
└── frontend/
    ├── Dockerfile                           # Frontend container definition (Nginx + Vite build)
    ├── index.html                           # HTML entry point
    ├── nginx.conf                           # Nginx config for serving the React app
    ├── package.json                         # Node dependencies (React, D3, Vite)
    ├── vite.config.js                       # Vite bundler configuration
    └── src/
        ├── main.jsx                         # React app entry point
        ├── App.jsx                          # Main UI – algorithm selector & compression form
        ├── index.css                        # Global styles
        └── components/
            ├── HuffmanTree.jsx              # D3.js interactive Huffman tree renderer
            └── StepFlow.jsx                 # Animated step-by-step compression flow UI
```

---

## 📖 About the Project

**Compression Visualizer** is an educational tool that makes it easy to understand how lossless data compression algorithms work — not just theoretically, but visually and interactively.

### What it does
- **Input any text** and compress it using one of four algorithms.
- **See the math** — every intermediate step of the compression process is shown in a clean, animated flow.
- **Visualize Huffman Trees** — for both Static and Dynamic Huffman encoding, an interactive tree is rendered directly in the browser using D3.js.
- **Compare algorithms** — observe differences in compression ratios and encoded outputs across methods.

### Algorithms covered

| Algorithm | Description |
|---|---|
| **Static Huffman** | Builds a fixed frequency table from the full input, then encodes. |
| **Dynamic Huffman** | Adapts the tree on-the-fly as each character is processed. |
| **Arithmetic Coding** | Encodes the entire message as a single floating-point number using probability intervals. |
| **LZW** | Dictionary-based compression that builds a codebook dynamically during encoding. |

### Tech Stack
- **Backend:** Python · FastAPI
- **Frontend:** React (Vite) · D3.js · Nginx
- **Deployment:** Docker · Docker Compose
