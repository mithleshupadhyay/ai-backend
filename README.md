## 🧠 AI-Powered Q&A Assistant

An intelligent, asynchronous question-answering system powered by **FastAPI**, **OpenAI**, **Celery**, **Gradio**, and **Redis**, with support for dynamic system prompts and context sourced from local files.

---

## 📂 Project Structure

```
ai-backend/
├── services/           # FastAPI backend + Celery task logic
├── demo/               # Gradio interface
├── files/              # Default context files (txt/pdf)
├── cache/              # Diskcache storage
├── .env                # Runtime secrets (ignored)
├── docker-compose.yml  # Multi-service orchestration
├── Makefile            # Developer shortcuts
└── start.sh            # Dev startup script
```

---

## 🚀 Features

- ✅ Asynchronous background question answering using **Celery**
- ✅ Context can be:
  - Provided directly in the request
  - Loaded automatically from `.txt` in `files/` if left blank
- ✅ Optional, editable and dynamic `system_prompt` per request
- ✅ Response caching with **Diskcache**
- ✅ Interactive frontend via **Gradio**
- ✅ Dockerized & ready for deployment

---

## 🛠️ Setup Instructions

### 1. Clone + Set Environment

```bash
git clone https://github.com/your-name/ai-backend.git
cd ai-backend
cp .env.template .env  # fill in your OpenAI key
```

### 2. Start via Docker Compose

```bash
docker-compose up --build
```

### 3. Or Start Manually (Dev mode)

```bash
# In separate terminals:
make api        # FastAPI (port 8000)
make worker     # Celery
make gradio     # Gradio UI (port 7860)
```

---

## 📮 API Reference

### POST `/ask`

```json
{
  "question": "Who is Mithlesh Upadhyay?",
  "context": "Mithlesh is a Senior AI Engineer working at XYZ.",
  "system_prompt": "Respond as a formal HR assistant for a job profile."
}
```

- Returns: 

```json
{
    "task_id": "89155f45-166d-4f5f-b067-0d187a0284a7",
    "status": "PENDING",
    "result": null
}
```

---

### POST `/result`

```json
{
  "task_id": "89155f45-166d-4f5f-b067-0d187a0284a7"
}
```

- Returns:
```json
{
    "task_id": "89155f45-166d-4f5f-b067-0d187a0284a7",
    "status": "SUCCESS",
    "result": "Mithlesh Upadhyay is a Senior AI Engineer currently employed at XYZ. He possesses expertise in artificial intelligence and plays a significant role in developing AI solutions for the organization. His contributions have been valuable in advancing the company's technological capabilities in the field of AI."
}
```

---

### GET `/health`

```json
{
    "status": "ok"
}
```

---

## 💬 Gradio UI

Open in browser:
```
http://localhost:7860
```

Enter:
- System prompt (editable)
- Context (optional)
- Question

---

## 🧠 Example Inputs / Outputs

### 🧾 Input:
```json
{
  "question": "What is Mithlesh's background?"
}
```
*(Context will be auto-loaded from `files/Mithlesh-Upadhyay.txt`)*

### ✅ Output:
```json
"Mithlesh Upadhyay is a Senior AI Engineer with expertise in..."
```

---

## 🧱 Architecture

- **FastAPI** handles API requests and validation
- **Celery** offloads long-running OpenAI completions
- **Redis** acts as a broker + result backend
- **Diskcache** stores repeated Q&A pairs
- **Gradio** provides user-friendly front-end interface
- **Docker** isolates services for scalable deployment

---

## 📦 Docker Usage

### Build & Run

```bash
docker-compose up --build
```

### Stop Services

```bash
docker-compose down
```

---

## 📜 Assumptions

- Files in `files/` are UTF-8 `.txt` 
- You provide a valid `OPENAI_API_KEY`
- System prompt is optional per-request, or defaults to a helpful assistant

---

## 🧪 Testing Endpoints

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the resume say about Mithlesh?"}'

curl -X POST http://localhost:8000/result \
  -H "Content-Type: application/json" \
  -d '{"task_id": "your-task-id"}'
```

---

## 🤝 Contributing

Pull requests are welcome! Please make sure to:

- Follow PEP8 formatting
- Include docstrings
- Add `.env.template` for new env vars

---

## 🧾 License

MIT © Mithlesh Upadhyay

---