from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from listings import get_listings_context
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_lead_email(name: str, email: str, context: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv("EMAIL_FROM")
        msg['To'] = os.getenv("EMAIL_TO")
        msg['Subject'] = f"New Lead: {name}"

        body = f"""
New lead from your website chatbot!

Name: {name}
Email: {email}

Last message context:
{context}

---
Sent automatically by your AI chatbot
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email error: {e}")

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

    # Check if lead was captured
    import re
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

    if emails_in_history and bot_asked_for_contact and request.session_id not in conversation_history.get('notified',
                                                                                                          []):
        # Extract name from history
        last_user_messages = [m['content'] for m in history if m['role'] == 'user']
        context = '\n'.join(last_user_messages[-3:])

        # Try to extract name from history
        user_messages = [m['content'] for m in history if m['role'] == 'user']
        potential_name = "Website Visitor"
        for msg in user_messages:
            words = msg.strip().split()
            if 1 <= len(words) <= 3 and not re.search(email_pattern, msg):
                potential_name = msg.strip()
                break

        send_lead_email(
            name=potential_name,
            email=emails_in_history[-1],
            context=context
        )

        # Mark as notified
        if 'notified' not in conversation_history:
            conversation_history['notified'] = []
        conversation_history['notified'].append(request.session_id)

    return {"reply": reply}