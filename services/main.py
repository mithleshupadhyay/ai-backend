from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import os
import uvicorn
import diskcache
import openai
from celery import Celery, states
from celery.exceptions import Ignore, Retry

# -----------------------------
# ENVIRONMENT VARIABLES
# -----------------------------

REDIS_BROKER_URL = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_BROKER_URL)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.getenv("CACHE_DIR", os.path.join(BASE_DIR, "cache"))
DEFAULT_CONTEXT_DIR = os.getenv("DEFAULT_CONTEXT_DIR", os.path.join(BASE_DIR, "files"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
DEFAULT_SYSTEM_PROMPT = os.getenv("DEFAULT_SYSTEM_PROMPT", "You are an intelligent Q&A assistant. Answer questions based only on the provided context.")

APP_PORT = int(os.getenv("APP_PORT", 8000))

openai.api_key = OPENAI_API_KEY


# -----------------------------
# INITIALIZATION
# -----------------------------
app = FastAPI()
cache = diskcache.Cache(CACHE_DIR)
celery_app = Celery("tasks", broker=REDIS_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# -----------------------------
# PYDANTIC MODELS
# -----------------------------
class QAPrompt(BaseModel):
    context: Optional[str] = Field(None, description="Context to ask questions from")
    question: str = Field(..., description="The question to answer from the context")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt to customize assistant behavior")
    task_id: Optional[str] = Field(None, description="Optional task ID to associate with the request")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None

class TaskRequest(BaseModel):
    task_id: str = Field(..., description="Task ID to retrieve the result")

# -----------------------------
# CONTEXT LOADER
# -----------------------------
def load_default_context() -> str:
    context_parts = []
    for filename in os.listdir(DEFAULT_CONTEXT_DIR):
        path = os.path.join(DEFAULT_CONTEXT_DIR, filename)
        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                context_parts.append(f.read())
    return "\n\n".join(context_parts)

# -----------------------------
# GEN AI LOGIC
# -----------------------------
def generate_answer(context: str, question: str, system_prompt: Optional[str]) -> str:
    prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
    ]
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=OPENAI_TEMPERATURE
    )
    return response.choices[0].message["content"].strip()

# -----------------------------
# CELERY BACKGROUND TASK WITH RETRY
# -----------------------------
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5}, retry_backoff=True)
def process_qa_task(self, context: Optional[str], question: str, system_prompt: Optional[str]) -> str:
    try:
        if not context:
            context = load_default_context()
        cache_key = f"{system_prompt}|{context}|{question}"
        if cache_key in cache:
            return cache[cache_key]
        answer = generate_answer(context, question, system_prompt)
        cache[cache_key] = answer
        return answer
    except openai.error.OpenAIError as e:
        raise self.retry(exc=e)
    except Exception as e:
        self.update_state(state=states.FAILURE, meta={'exc': str(e)})
        raise Ignore()

# -----------------------------
# FASTAPI ENDPOINTS
# -----------------------------
@app.post("/ask", response_model=TaskResponse)
async def ask_question(prompt: QAPrompt):
    task_id = prompt.task_id or str(uuid.uuid4())
    task = process_qa_task.apply_async(args=[prompt.context, prompt.question, prompt.system_prompt], task_id=task_id)
    return TaskResponse(task_id=task.id, status="PENDING")

@app.post("/result", response_model=TaskResponse)
async def get_result(request: TaskRequest):
    task_result = celery_app.AsyncResult(request.task_id)
    if not task_result:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        response = TaskResponse(task_id=request.task_id, status=task_result.status)
        if task_result.successful():
            response.result = task_result.result
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=True)


