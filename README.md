# AI PDF Chatbot — Landon Hotel Night Manager

A context-grounded hotel chatbot that answers guest questions strictly using information extracted from a PDF document. Built with Flask and connected to Eli Lilly's internal LLM Gateway via Azure AD authentication.

## Features

- **PDF-grounded answers** — extracts hotel info from a PDF at startup; the LLM is forbidden from hallucinating
- **Azure AD OAuth2 authentication** — auto-refreshes Bearer tokens before expiry
- **Web UI** — clean chat interface served by Flask (`templates/index.html`)
- **CLI mode** — `main.py` for quick terminal-based interaction
- **Secure config** — all credentials loaded from `.env`, never hardcoded

## Architecture

```
User Browser
     │
     ▼
Flask (app.py)
     │  loads context from pdf_text.txt
     │  formats prompt with hotel_assistant_template
     ▼
llm_gateway.py
     │  fetches OAuth2 token from Azure AD
     │  builds OpenAI client → Lilly LLM Gateway
     ▼
GPT model response → JSON → Browser
```

## Project Structure

```
AIChatbot/
├── app.py                  # Flask web application & /chat endpoint
├── main.py                 # CLI chatbot (stdin/stdout)
├── llm_gateway.py          # Azure AD auth + OpenAI client factory
├── templates/
│   └── index.html          # Chat UI
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── .gitignore
```

> **Note:** `Landon-Hotel.pdf` and the extracted `pdf_text.txt` are excluded from source control (large files). Place your own PDF in the project root before running.

## Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/L036841/AI_PDF_Chatbot_Hotel.git
cd AI_PDF_Chatbot_Hotel
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env and fill in your Azure AD and LLM Gateway credentials
```

| Variable | Description |
|---|---|
| `CLIENT_ID` | Azure AD application (client) ID |
| `CLIENT_SECRET` | Azure AD client secret |
| `TENANT_ID` | Azure AD tenant ID |
| `LLM_GATEWAY_KEY` | Lilly LLM Gateway API key |
| `GATEWAY_BASE_URL` | LLM Gateway base URL |
| `GATEWAY_SCOPE` | OAuth2 scope for the gateway |
| `DEFAULT_MODEL` | Model name (e.g. `gpt-5.1-2025-11-13`) |

### 3. Add your PDF

Place your hotel information PDF in the project root:

```
AIChatbot/
└── Landon-Hotel.pdf   ← your file here
```

### 4. Run

**Web app:**
```bash
python app.py
# Open http://localhost:5000
```

**CLI:**
```bash
python main.py
```

## How It Works

1. On startup, `app.py` extracts all text from `Landon-Hotel.pdf` via PyMuPDF and caches it to `pdf_text.txt`.
2. Every `/chat` POST request formats a strict prompt template that injects the full hotel context.
3. The LLM is instructed to answer **only** from the provided context — it responds with _"I don't have that information"_ when the answer isn't in the PDF.
4. `llm_gateway.py` transparently refreshes the Azure AD OAuth2 token before each request if it has expired.

## Security Notes

- Credentials are **never** committed to source control — use `.env` (see `.env.example`)
- SSL verification is disabled for the internal gateway (`verify=False`) — acceptable on the internal Lilly network
- The chatbot's system prompt enforces strict hallucination prevention

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3.1 |
| LLM client | OpenAI Python SDK |
| Authentication | Azure AD OAuth2 (`requests`) |
| HTTP client | httpx |
| PDF extraction | PyMuPDF (fitz) |
| Frontend | Vanilla HTML/CSS/JS |
