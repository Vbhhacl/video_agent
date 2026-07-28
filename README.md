\<div align="center">

# 🎬 AI Video Assistant

### *Meeting Intelligence — Transcribe · Summarise · Chat with your meetings*

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Mistral AI](https://img.shields.io/badge/Mistral_AI-small--latest-FF6F00?logo=mistral&logoColor=white)](https://mistral.ai/)
[![Whisper](https://img.shields.io/badge/OpenAI_Whisper-small-412991?logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5%2B-FE7F2D?logo=chromadb&logoColor=white)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()

---

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Pipeline Stages](#-pipeline-stages)
  - [1. Audio Acquisition & Processing](#1-audio-acquisition--processing)
  - [2. Speech-to-Text Transcription](#2-speech-to-text-transcription)
  - [3. Title Generation](#3-title-generation)
  - [4. Summarisation (Map-Reduce)](#4-summarisation-map-reduce)
  - [5. Structured Extraction](#5-structured-extraction)
  - [6. RAG-Powered Q&A Chat](#6-rag-powered-qa-chat)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the App](#running-the-app)
- [Usage Guide](#-usage-guide)
  - [Web Interface (Streamlit)](#web-interface-streamlit)
  - [Command-Line Interface (CLI)](#command-line-interface-cli)
- [API Keys & Services](#-api-keys--services)
- [Security Notes](#-security-notes)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**AI Video Assistant** is a full-stack intelligent meeting assistant that transforms raw video/audio content into structured, actionable insights. It supports both **YouTube URLs** and **local media files**, processes them through an automated pipeline, and delivers:

- Accurate **transcriptions** (English via Whisper, Hinglish→English via Sarvam AI)
- Professional **meeting summaries** using a map-reduce LLM approach
- **Action items** with owners and deadlines
- **Key decisions** made during the meeting
- **Open questions** requiring follow-up
- An interactive **RAG-powered chatbot** to ask questions about the transcript

The system uses **Mistral AI** (via LangChain) for all LLM operations, **ChromaDB** for vector storage, and **HuggingFace embeddings** (all-MiniLM-L6-v2) for semantic retrieval.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🎵 Dual Input Sources** | YouTube URLs (via `yt-dlp`) or local video/audio files |
| **🗣️ Bilingual STT** | English via OpenAI Whisper (local), Hinglish→English via Sarvam AI API |
| **🏷️ Smart Title Gen** | Automatically generates concise, professional meeting titles (≤8 words) |
| **📋 Map-Reduce Summary** | Handles unlimited-length transcripts by chunking, summarising, and combining |
| **✅ Structured Extraction** | Extracts action items (with owners/deadlines), key decisions, and open questions |
| **💬 RAG Chat** | Ask natural-language questions about the transcript with context-aware answers |
| **🖥️ Dual Interface** | Rich Streamlit web UI + lightweight CLI |
| **🌓 Dark Cyber UI** | Custom-styled dark theme with gradient accents, live pipeline status, and card-based layout |
| **📄 Export Support** | PDF/TXT export capabilities (via `reportlab` / `fpdf2`) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INPUT SOURCES                                │
│            YouTube URL  │  Local File (.mp4/.mp3/.wav/...)          │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│               AUDIO PROCESSING  (utils/audio_processor.py)          │
│                                                                     │
│   ┌──────────────┐    ┌──────────────┐    ┌───────────────────┐    │
│   │ yt-dlp       │───▶│ convert_to_  │───▶│ chunk_audio       │    │
│   │ download     │    │ wav (16kHz   │    │ (10-min segments) │    │
│   └──────────────┘    │ mono)        │    └───────────────────┘    │
│                       └──────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│               TRANSCRIPTION  (core/transcriber.py)                  │
│                                                                     │
│   ┌──────────────────────┐   ┌──────────────────────────────┐      │
│   │ English → Whisper    │   │ Hinglish → Sarvam AI API     │      │
│   │ (local model)        │   │ (auto-translates to English) │      │
│   └──────────────────────┘   └──────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│              LLM PIPELINE  (LangChain → Mistral AI)                 │
│                                                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│   │ Title Gen    │  │ Map-Reduce   │  │ Structured Extraction  │   │
│   │ (≤8 words)   │  │ Summariser   │  │ (Items/Decisions/Q's)  │   │
│   └──────────────┘  └──────────────┘  └────────────────────────┘   │
│                                                                     │
│   ┌────────────────────────────────────────────────────────────┐    │
│   │ RAG Engine (Vector Store + Retriever + QA Chain)           │    │
│   │ ChromaDB ◀─── HuggingFace Embeddings ◀─── Mistral AI      │    │
│   └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INTERFACES                                       │
│                                                                     │
│   ┌─────────────────────────┐    ┌──────────────────────────┐      │
│   │  Streamlit Web UI       │    │  CLI (main.py)           │      │
│   │  (app.py)               │    │  Interactive chat loop   │      │
│   └─────────────────────────┘    └──────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Core AI & ML
| Technology | Purpose |
|------------|---------|
| **[OpenAI Whisper](https://github.com/openai/whisper)** (small model) | Local English speech-to-text |
| **[Sarvam AI API](https://www.sarvam.ai/)** (saaras:v2.5) | Hinglish speech-to-text with English translation |
| **[Mistral AI](https://mistral.ai/)** (mistral-small-latest) | LLM for summarisation, extraction, and QA |
| **[LangChain](https://www.langchain.com/)** (LCEL) | LLM orchestration, prompt chains, RAG pipelines |
| **[HuggingFace Embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)** (all-MiniLM-L6-v2) | Semantic text embeddings |
| **[ChromaDB](https://www.trychroma.com/)** | Local vector database for RAG retrieval |

### Audio & Video
| Technology | Purpose |
|------------|---------|
| **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** | YouTube audio download |
| **[pydub](https://github.com/jiaaro/pydub)** | Audio format conversion & chunking |
| **[FFmpeg](https://ffmpeg.org/)** | Audio codec processing (required separately) |

### Frontend & Utilities
| Technology | Purpose |
|------------|---------|
| **[Streamlit](https://streamlit.io/)** | Web UI framework |
| **Python-dotenv** | Environment variable management |
| **deep-translator** | Lightweight translation support |
| **reportlab / fpdf2** | PDF export capabilities |
| **tqdm** | Progress bar utilities |

---

## 📁 Project Structure

```
📦 Video_Agent/
├── app.py                      # Streamlit web application (main UI)
├── main.py                     # CLI entry point (interactive pipeline)
├── test.py                     # Test/demo script (quick pipeline run)
├── requirements.txt            # Python dependencies
├── .env                        # 🔒 API keys (NOT committed)
├── .env.example                # Template for environment variables
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── core/                       # 🔧 Core processing modules
│   ├── transcriber.py          #   Speech-to-text (Whisper / Sarvam)
│   ├── summarizer.py           #   Title gen + map-reduce summarisation
│   ├── extractor.py            #   Action items, decisions, questions extraction
│   ├── rag_engine.py           #   RAG chain construction & QA
│   └── vector_store.py         #   ChromaDB vector store management
│
├── utils/                      # 🛠️ Utility modules
│   └── audio_processor.py      #   YouTube download, WAV conversion, audio chunking
│
├── vector_db/                  # 📊 Persistent ChromaDB vector store (auto-generated)
│
└── downloads/                  # 📥 Downloaded/cached audio files (auto-generated)
```

---

## 🔄 Pipeline Stages

### 1. Audio Acquisition & Processing
**Module:** `utils/audio_processor.py`

Detects source type and prepares audio for transcription:
- **YouTube URLs** → Downloads best audio quality via `yt-dlp` and extracts to 16kHz mono WAV using FFmpeg
- **Local files** → Converts to 16kHz mono WAV via `pydub`
- Splits audio into **10-minute chunks** for efficient processing

### 2. Speech-to-Text Transcription
**Module:** `core/transcriber.py`

Routes audio chunks based on language selection:
- **English** → Processed locally with **OpenAI Whisper** (small model; ~1.5GB VRAM)
- **Hinglish** → Sent to **Sarvam AI API** which transcribes and translates Hindi-English mixed speech to English. Audio is further split into 25-second pieces (Sarvam's 30s limit) before sending.

### 3. Title Generation
**Module:** `core/summarizer.py` → `generate_title()`

Uses Mistral AI to generate a concise, professional meeting title (max 8 words) from the first 2000 characters of the transcript.

### 4. Summarisation (Map-Reduce)
**Module:** `core/summarizer.py` → `summarize()`

Handles transcripts of arbitrary length using a two-phase approach:
1. **Map Phase:** Splits the full transcript into 3000-character chunks (200-char overlap) and summarises each independently
2. **Reduce Phase:** Combines all chunk summaries and generates a single cohesive, bullet-pointed meeting summary

### 5. Structured Extraction
**Module:** `core/extractor.py`

Three dedicated LLM chains extract structured information:
- **Action Items** → Task description, owner, and deadline (numbered list)
- **Key Decisions** → Major decisions made during the meeting
- **Open Questions** → Unresolved topics requiring follow-up

### 6. RAG-Powered Q&A Chat
**Modules:** `core/vector_store.py`, `core/rag_engine.py`

Enables natural-language conversation with the transcript:
1. **Chunking:** Transcript split into 500-character segments (50-char overlap)
2. **Embedding:** Each chunk embedded with `all-MiniLM-L6-v2` via HuggingFace
3. **Indexing:** Stored in a local **ChromaDB** vector database
4. **Retrieval:** Top-4 most relevant chunks retrieved via cosine similarity
5. **Generation:** Mistral AI answers based exclusively on retrieved context

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **FFmpeg** (required by `pydub` and `yt-dlp`) — [Install FFmpeg](https://ffmpeg.org/download.html)
  - *Windows:* Download from the official site or use `winget install ffmpeg`
  - *macOS:* `brew install ffmpeg`
  - *Linux:* `sudo apt install ffmpeg`
- **Mistral AI API Key** — [Get one here](https://console.mistral.ai/)
- **Sarvam AI API Key** *(optional — only for Hinglish transcription)* — [Get one here](https://www.sarvam.ai/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Video_Agent.git
cd Video_Agent

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
# Option A: Using pip
pip install -r requirements.txt

# Option B: Using uv (faster)
uv pip install -r requirements.txt
```

### Configuration

```bash
# 1. Create your environment file from the template
cp .env.example .env          # macOS / Linux
copy .env.example .env        # Windows

# 2. Edit .env and fill in your API keys
```

**Required `.env` variables:**
```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

**Optional `.env` variables:**
```env
SARVAM_API_KEY=your_sarvam_api_key_here    # Required only for Hinglish transcription
WHISPER_MODEL=small                        # Whisper model size (tiny/base/small/medium/large)
```

### Running the App

#### 🖥️ Web Interface (Streamlit)
```bash
streamlit run app.py
```
Opens at `http://localhost:8501` — paste a YouTube URL or file path in the sidebar and click **Analyse**.

#### ⌨️ Command-Line Interface
```bash
python main.py
```
Follow the prompts to enter a source and language, then chat interactively with the results.

#### 🧪 Quick Test
```bash
python test.py
```
Runs the full pipeline on a pre-configured source (edit `test.py` to change).

---

## 📖 Usage Guide

### Web Interface (Streamlit)

The Streamlit UI (`app.py`) delivers a fully custom dark-themed experience with cyberpunk-inspired styling. Here's how to use it:

#### 🎨 UI Layout

The interface is split into two main areas:

**📍 Sidebar (Left Panel)**
- **Brand header** — "AI Video" logo with "Meeting Intelligence" subtitle
- **Input section** — Text field for YouTube URL or local file path
- **Language selector** — Dropdown (`english` / `hinglish`)
- **Analyse button** — ⚡ Analyse triggers the full pipeline
- **Pipeline status panel** — After analysis, shows live step indicators (audio, transcript, title, summary, extraction, RAG) with animated dots:
  - 🟣 *Pulsing dot* = currently processing
  - 🟢 *Solid dot* = completed
  - ⚫ *Dim dot* = pending

**📍 Main Content Area**
- **Hero section** — Gradient title "AI Video Assistant" with subtitle
- **Results cards** (post-analysis):
  - 📌 **Session Title** — Full-width card with generated meeting title
  - 📋 **Summary** — Left column card with professional meeting summary
  - 📝 **Full Transcript** — Right column collapsible expander with scrollable transcript
  - ✅ **Action Items** — 3-column card showing tasks with owners & deadlines
  - 🔑 **Key Decisions** — Major decisions made during the meeting
  - ❓ **Open Questions** — Unresolved topics needing follow-up
- **Chat section** — RAG-powered Q&A at the bottom:
  - Chat history display with styled user/assistant bubbles
  - Text input + Send button
  - Clear Chat button to reset conversation
- **Empty state** — When no session is loaded, displays a centred welcome message with feature badges

#### 🖱️ Step-by-Step Usage

1. **Open** `http://localhost:8501` in your browser
2. **Enter input** in the sidebar:
   - Paste a **YouTube URL** (e.g., `https://youtube.com/watch?v=...`)
   - Or enter a **local file path** (e.g., `C:\meetings\recording.mp4`)
3. **Select language** — `english` (Whisper) or `hinglish` (Sarvam AI)
4. Click **⚡ Analyse** to start the pipeline
5. **Monitor progress** via the sidebar's live step indicators:
   - 🔊 Audio Processing
   - 📝 Transcription
   - 🏷️ Title Generation
   - 📋 Summarisation
   - 🔍 Extraction
   - 🧠 RAG Engine
6. **Review results** in the main content area
7. **Chat with the meeting** — Type questions in the chat input at the bottom (e.g., *"What were the main decisions made?"*)
8. **Clear chat** using the 🗑️ Clear Chat button to start a fresh Q&A session

### Command-Line Interface (CLI)

```bash
python main.py
# Enter YouTube URL or local file path: https://youtube.com/watch?v=...
# Language (english/hinglish): english
```

After processing, you enter an interactive Q&A loop:
```
💬 Chat with your meeting (type 'exit' to quit)

You: What were the main decisions made?
🤖 Assistant: [Answer based on transcript]

You: Who is responsible for the design task?
🤖 Assistant: [Context-aware answer]

You: exit
👋 Goodbye!
```

---

## 🔑 API Keys & Services

| Service | Required? | Cost | Obtain |
|---------|-----------|------|--------|
| **Mistral AI** | ✅ Yes | Free tier available (~500M tokens/month) | [console.mistral.ai](https://console.mistral.ai/) |
| **Sarvam AI** | ⚠️ Only for Hinglish | Paid (usage-based) | [www.sarvam.ai](https://www.sarvam.ai/) |
| **OpenAI Whisper** | ❌ No (runs locally) | Free | Included via `openai-whisper` pip package |

> **Note:** Whisper runs entirely on your local machine — no internet connection needed for English transcription. The small model requires ~1.5GB of VRAM (GPU) or ~2GB of RAM (CPU).

---

## 🔒 Security Notes

- The `.env` file contains sensitive API keys and is **ignored by Git** (via `.gitignore`)
- Use `.env.example` as a template — never commit actual credentials
- The `vector_db/` directory is auto-generated and Git-ignored
- The `downloads/` directory stores cached audio; clean it periodically
- All processing runs locally except API calls to Mistral AI and (optionally) Sarvam AI

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate documentation.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by the AI Video Assistant Team

</div>

