# 🤖 Autonomous Research Agent

> **AI that researches any topic automatically** — searches the internet, reads articles, summarizes with LLM, stores in vector DB, and generates professional outputs.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green?logo=openai)](https://openai.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange)](https://ollama.ai)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-purple)](https://chromadb.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 What It Does

Give the agent a **topic** → it autonomously:

```
User: "AI impact on healthcare in 2025"
         ↓
🔍 Searches internet (DuckDuckGo, no API key needed)
         ↓
📰 Reads & scrapes 8+ articles
         ↓
✍️  Summarizes each article with LLM
         ↓
🗄️  Stores in ChromaDB vector database
         ↓
🧠 Synthesizes all findings
         ↓
📄 Generates: Research Paper | Blog Post | Slides
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Autonomous Search** | Uses DuckDuckGo — no API key required |
| 📰 **Smart Web Scraping** | Extracts clean article content with BeautifulSoup |
| 🧠 **LLM Summarization** | Per-article summaries + cross-source synthesis |
| 🗄️ **Vector DB (RAG)** | ChromaDB with sentence-transformer embeddings |
| 📑 **Research Paper** | Formal academic-style Markdown report |
| 📝 **Blog Post** | Engaging, readable blog in Markdown |
| 🎯 **Slides** | Reveal.js HTML presentation |
| 💬 **Follow-up Q&A** | Ask questions, answered via RAG |
| 🦙 **Ollama Support** | Run 100% locally — no cloud required |
| 🖥️ **Streamlit UI** | Beautiful web interface |

---

## 🏗️ Architecture

```
autonomous-research-agent/
│
├── agent/
│   ├── __init__.py           # Package exports
│   ├── research_agent.py     # 🤖 Main orchestrator agent
│   ├── web_scraper.py        # 🌐 DuckDuckGo search + BeautifulSoup scraping
│   ├── summarizer.py         # 🧠 LLM summarization & synthesis (OpenAI/Ollama)
│   ├── vector_store.py       # 🗄️ ChromaDB vector database + RAG retrieval
│   └── report_generator.py   # 📄 Report / Blog / Slides generator
│
├── app.py                    # 🖥️ Streamlit web UI
├── main.py                   # 💻 CLI entry point
├── requirements.txt          # 📦 Dependencies
├── .env.example              # ⚙️ Environment variables template
└── outputs/                  # 📁 Generated research outputs
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/PranayMahendrakar/autonomous-research-agent.git
cd autonomous-research-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 4. Run the Web UI
```bash
streamlit run app.py
```

### 5. Or use the CLI
```bash
# Research paper
python main.py --topic "Impact of AI on healthcare" --format report

# Blog post
python main.py --topic "Quantum computing advances 2025" --format blog

# Presentation slides
python main.py --topic "Climate change solutions" --format slides --sources 10

# With follow-up question
python main.py --topic "Machine learning trends" --ask "What are the key challenges?"
```

---

## 🦙 Use with Ollama (100% Local — Free!)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2

# Run with Ollama
python main.py --topic "Renewable energy" --ollama --ollama-model llama3.2
```

Or in `.env`:
```
USE_OLLAMA=true
OLLAMA_MODEL=llama3.2
```

---

## 📄 Output Examples

### Research Paper (Markdown)
```markdown
# AI in Healthcare — Research Report
## Abstract
...
## Key Findings
...
## Analysis & Discussion
...
## References
1. [Source 1](https://example.com) — example.com
```

### Presentation Slides (HTML)
Opens in any browser with animated Reveal.js slides featuring:
- Title slide with topic
- Findings slides with bullet points
- Dark gradient themes
- Smooth transitions

### Blog Post (Markdown)
Engaging, readable format with headers, bullet points, and citations.

---

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Your OpenAI API key |
| `OPENAI_MODEL` | gpt-4o-mini | OpenAI model name |
| `USE_OLLAMA` | false | Use local Ollama instead |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server URL |
| `OLLAMA_MODEL` | llama3.2 | Ollama model name |
| `MAX_TOKENS` | 1500 | Max LLM response tokens |
| `MAX_SOURCES` | 8 | Default web sources count |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | OpenAI GPT-4o / GPT-4o-mini / Ollama (llama3.2, mistral, etc.) |
| **Web Search** | DuckDuckGo Search (free, no API key) |
| **Web Scraping** | Requests + BeautifulSoup4 |
| **Vector DB** | ChromaDB with sentence-transformers embeddings |
| **Embeddings** | all-MiniLM-L6-v2 (runs locally, no API needed) |
| **Web UI** | Streamlit |
| **Output** | Markdown (reports/blogs) + Reveal.js HTML (slides) |

---

## 📋 CLI Reference

```
python main.py [OPTIONS]

Options:
  --topic, -t    Research topic (required)
  --format, -f   Output: report | blog | slides (default: report)
  --sources, -s  Number of sources to use (default: 8)
  --output, -o   Output directory (default: ./outputs)
  --api-key      OpenAI API key (or use env var)
  --ollama        Use local Ollama
  --ollama-model  Ollama model name (default: llama3.2)
  --ask, -a      Follow-up question after research
```

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ by [Pranay M Mahendrakar](https://sonytech.in/pranay/) | Powered by LLM Agents + Web Scraping + Vector DB*
