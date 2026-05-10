from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from listings import get_listings_context
import os

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")

SYSTEM_PROMPT = f"""You are a helpful real estate assistant for a agency in Austin, TX.
You help potential buyers find their perfect home.

{get_listings_context()}

Your job:
- Answer questions about available properties
- Help narrow down options based on budget, bedrooms, location preferences
- Be friendly and professional
- If someone is interested in a property or wants to schedule a viewing, ask for their name and email
- Keep responses concise and helpful

If asked about anything unrelated to real estate, politely redirect the conversation."""

conversation_history = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat(request: ChatRequest):
    if request.session_id not in conversation_history:
        conversation_history[request.session_id] = []

    history = conversation_history[request.session_id]
    history.append({"role": "user", "content": request.message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        max_tokens=500,
        temperature=0.7
    )

    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})

    # Keep history manageable
    if len(history) > 20:
        conversation_history[request.session_id] = history[-20:]

    return {"reply": reply}