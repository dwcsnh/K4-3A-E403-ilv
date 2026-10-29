# Cách chạy code (Dev environment, Ubuntu)

## Agents project

**Bước 1: Di chuyển vào thư mục agents**
```bash
cd codebase/agents
```

**Tạo file .env**

Tạo file .env với nội dung sau, paste openai_api_key vào

```bash
# Day 04 Lab v3 — IT Helpdesk Agent
# Copy this file to `.env` (same folder) and fill in your keys.
# NEVER commit `.env` — it is gitignored. Keys here are NAMES ONLY (no values).

# --- Model provider (choose ONE; OpenRouter recommended) ---
# OPENROUTER_API_KEY=
OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# GEMINI_API_KEY=

# Helpdesk tools use deterministic local mock data and need no additional keys.

# --- Optional external device search (Tavily) ---
TAVILY_API_KEY=

```

**Bước 2: Tạo và kích hoạt virtual environment**

Linux/Mac OS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Bước 3: Cài đặt các thư viện cần thiết**
```bash
pip install -r requirements.txt
```

**Bước 4: Chạy server**

Backend cần MongoDB chạy ở `mongodb://localhost:27017` (đổi bằng biến `CLASSROOM_MONGODB_URI`).

```bash
python classroom_gateway.py
```

Server lắng nghe HTTP và WebSocket (`/ws/classroom`) ở cổng `8000`.

## Frontend project

**Bước 1: Di chuyển vào thư mục frontend**
```bash
cd codebase/frontend
```

**Bước 2: Cài đặt các thư viện cần thiết**
```bash
npm install
```

**Bước 3: Chạy server**
```bash
npm run dev
```

Mở trang web ở `http://localhost:3000/` hoặc url được log trong terminal