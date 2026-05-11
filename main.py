from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from listings import get_listings_context
import os
import re
import resend


def send_lead_email(name: str, email: str, context: str):
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")

        params = {
            "from": "Real Estate Bot <onboarding@resend.dev>",
            "to": os.getenv("EMAIL_TO"),
            "subject": f"New Lead: {name}",
            "html": f"""
                <h2>New lead from your website chatbot!</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <h3>Conversation context:</h3>
                <p>{context.replace(chr(10), '<br>')}</p>
                <hr>
                <p><em>Sent automatically by your AI chatbot</em></p>
            """
        }

        resend.Emails.send(params)
        print(f"Email sent successfully to {os.getenv('EMAIL_TO')}")
    except Exception as e:
        print(f"Email error: {e}")

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")

SYSTEM_PROMPT = f"""You are a helpful real estate assistant for an agency in Austin, TX.
You help potential buyers find their perfect home.

{get_listings_context()}

IMPORTANT RULES:
- If this is the user's FIRST message and you don't know their name yet, ALWAYS respond with exactly: "Thank you. May I ask who I have the pleasure of speaking with?"
- Once you know their name, use it naturally in responses
- When buyer asks for properties "under $X" — show ALL properties with price LESS THAN $X
- If someone is interested in a property or wants to schedule a viewing, ask for their email
- Keep responses concise and helpful
- Answer questions about available properties accurately
- If the first message contains [CONTEXT: Customer selected "X"], use that as the customer's primary interest. Focus responses on that topic first, but still help with any real estate question if asked.
- Never mention or show the [CONTEXT] tag to the user

If asked about anything unrelated to real estate, politely redirect the conversation."""

conversation_history = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
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

    # Check if lead was captured
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails_in_history = []

    for msg in history:
        if msg['role'] == 'user':
            found_emails = re.findall(email_pattern, msg['content'])
            emails_in_history.extend(found_emails)

    bot_asked_for_contact = any(
        any(phrase in m['content'].lower() for phrase in ['your name', 'your email', 'name and email', 'contact'])
        for m in history if m['role'] == 'assistant'
    )

    print(f"DEBUG emails: {emails_in_history}, bot_asked: {bot_asked_for_contact}")

    notified = conversation_history.get('notified', [])

    if emails_in_history and bot_asked_for_contact and request.session_id not in notified:
        # Extract context
        last_user_messages = [m['content'] for m in history if m['role'] == 'user']
        context = '\n'.join(last_user_messages[-3:])

        # Try to extract name from history
        potential_name = "Website Visitor"
        for msg in last_user_messages:
            words = msg.strip().split()
            if 1 <= len(words) <= 3 and not re.search(email_pattern, msg):
                potential_name = msg.strip()
                break

        print(f"DEBUG sending email: name={potential_name}, email={emails_in_history[-1]}")

        background_tasks.add_task(
            send_lead_email,
            potential_name,
            emails_in_history[-1],
            context
        )

        # Mark as notified
        if 'notified' not in conversation_history:
            conversation_history['notified'] = []
        conversation_history['notified'].append(request.session_id)

    return {"reply": reply}
