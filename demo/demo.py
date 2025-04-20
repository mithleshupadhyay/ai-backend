import gradio as gr
import requests
import time
import os

API_ASK_URL = os.getenv("API_ASK_URL", "http://localhost:8000/ask")
API_RESULT_URL = os.getenv("API_RESULT_URL", "http://localhost:8000/result")
GRADIO_PORT = int(os.getenv("GRADIO_PORT", 7860))


def submit_question(system_prompt, context, question):
    system_prompt = system_prompt.strip()
    context_to_send = context.strip() if context.strip() else None

    ask_payload = {
        "question": question,
        "context": context_to_send,
        "system_prompt": system_prompt
    }

    try:
        ask_response = requests.post(API_ASK_URL, json=ask_payload)
        ask_response.raise_for_status()
        task_id = ask_response.json()["task_id"]
    except Exception as e:
        return f"Error submitting question: {e}"

    # Poll for result
    result_payload = {"task_id": task_id}
    for _ in range(30):
        time.sleep(1.5)
        try:
            result_response = requests.post(API_RESULT_URL, json=result_payload)
            result_response.raise_for_status()
            result_data = result_response.json()
            if result_data["status"] == "SUCCESS":
                return result_data["result"]
        except Exception as e:
            return f"Error getting result: {e}"

    return "Request timed out. Please try again later."


demo = gr.Interface(
    fn=submit_question,
    inputs=[
        gr.Textbox(label="System Prompt", value="You are an intelligent Q&A assistant. Answer questions based only on the provided context.", lines=3),
        gr.Textbox(label="Context (leave blank to use file-based context)", lines=10, placeholder="Paste custom context or leave blank..."),
        gr.Textbox(label="Question", placeholder="Ask a question about the context", lines=2)
    ],
    outputs=gr.Textbox(label="Answer", lines=5),
    title="Q&A Assistant with Dynamic Prompt and Context",
    description="Ask questions using custom or file-based context. Powered by OpenAI, FastAPI, Celery, and Diskcache."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=GRADIO_PORT, share=True)
