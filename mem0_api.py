from fastapi import FastAPI
from pydantic import BaseModel
from mem0 import Memory
import os
from openai import OpenAI

app = FastAPI()

# Use persistent Chroma in Railway’s persistent volume (later)
PERSIST_DIR = "./memories"
os.makedirs(PERSIST_DIR, exist_ok=True)

memory = Memory.from_config({
    "vector_store": {
        "provider": "chroma",
        "config": {
            "persist_directory": PERSIST_DIR
        }
    },
    "version": "v1.1"
})

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatInput(BaseModel):
    message: str
    user_id: str = "default_user"

@app.post("/chat")
def chat(input: ChatInput):
    relevant = memory.search(query=input.message, user_id=input.user_id, limit=3)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant["results"])

    system_prompt = f"You are a helpful AI. User memories:\n{memories_str}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input.message}
    ]

    res = openai_client.chat.completions.create(model="gpt-4o", messages=messages)
    reply = res.choices[0].message.content

    messages.append({"role": "assistant", "content": reply})
    memory.add(messages, user_id=input.user_id)

    return {"response": reply}
