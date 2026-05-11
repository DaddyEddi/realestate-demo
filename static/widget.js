(function() {
    const BACKEND_URL = "https://realestate-demo-production.up.railway.app";

    const style = document.createElement("style");
    style.textContent = `
        #arq-toggle {
            position: fixed; bottom: 28px; right: 28px;
            width: 60px; height: 60px;
            background: #e94560; border-radius: 50%;
            border: none; cursor: pointer;
            font-size: 26px; color: white;
            box-shadow: 0 4px 20px rgba(233,69,96,0.5);
            z-index: 99999; transition: transform 0.2s;
        }
        #arq-toggle:hover { transform: scale(1.1); }
        #arq-window {
            position: fixed; bottom: 100px; right: 28px;
            width: 360px; height: 520px;
            background: white; border-radius: 16px;
            box-shadow: 0 8px 40px rgba(0,0,0,0.15);
            display: none; flex-direction: column;
            z-index: 99999; overflow: hidden;
            font-family: 'Segoe UI', sans-serif;
        }
        #arq-window.arq-open { display: flex; }
        .arq-header {
            background: #1a1a2e; color: white;
            padding: 16px 20px;
            display: flex; align-items: center; gap: 12px;
        }
        .arq-avatar {
            width: 36px; height: 36px;
            background: #e94560; border-radius: 50%;
            display: flex; align-items: center;
            justify-content: center; font-size: 18px;
        }
        .arq-header-info h4 { font-size: 15px; margin: 0; }
        .arq-header-info p { font-size: 12px; color: #aaa; margin: 0; }
        .arq-dot { width: 8px; height: 8px; background: #4caf50; border-radius: 50%; display: inline-block; margin-right: 4px; }
        #arq-messages {
            flex: 1; overflow-y: auto;
            padding: 16px;
            display: flex; flex-direction: column; gap: 12px;
        }
        .arq-msg {
            max-width: 80%; padding: 10px 14px;
            border-radius: 12px; font-size: 14px; line-height: 1.5;
        }
        .arq-msg.bot { background: #f0f0f0; color: #333; align-self: flex-start; border-bottom-left-radius: 4px; }
        .arq-msg.user { background: #e94560; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .arq-input-area {
            padding: 12px 16px; border-top: 1px solid #eee;
            display: flex; gap: 8px;
        }
        #arq-input {
            flex: 1; border: 1px solid #ddd;
            border-radius: 24px; padding: 10px 16px;
            font-size: 14px; outline: none;
        }
        #arq-input:focus { border-color: #e94560; }
        #arq-send {
            background: #e94560; color: white;
            border: none; width: 40px; height: 40px;
            border-radius: 50%; cursor: pointer; font-size: 18px;
        }
        #arq-send:hover { background: #c73652; }
    `;
    document.head.appendChild(style);

    document.body.innerHTML += `
        <button id="arq-toggle">💬</button>
        <div id="arq-window">
            <div class="arq-header">
                <div class="arq-avatar">🤖</div>
                <div class="arq-header-info">
                    <h4>Realty Assistant</h4>
                    <p><span class="arq-dot"></span>Online · AI Powered</p>
                </div>
            </div>
            <div id="arq-messages"></div>
            <div class="arq-input-area">
                <input type="text" id="arq-input" placeholder="Ask about properties..." />
                <button id="arq-send">➤</button>
            </div>
        </div>
    `;

    let sessionId = localStorage.getItem('arq_session_id');
    if (!sessionId) {
        sessionId = Math.random().toString(36).substr(2, 9);
        localStorage.setItem('arq_session_id', sessionId);
    }
    let greeted = localStorage.getItem('arq_greeted') === 'true';

    function toggleChat() {
        const win = document.getElementById("arq-window");
        win.classList.toggle("arq-open");
        if (win.classList.contains("arq-open") && !greeted) {
            greeted = true;
            localStorage.setItem('arq_greeted', 'true');
            setTimeout(() => addMessage("bot", "Hi! 👋 I'm your Realty AI assistant. I can help you find the perfect home, answer questions about listings, or schedule a viewing. What are you looking for?"), 400);
        }
    }

    function addMessage(role, text) {
        const msgs = document.getElementById("arq-messages");
        const div = document.createElement("div");
        div.className = `arq-msg ${role}`;
        div.textContent = text;
        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
        return div;
    }

    async function sendMessage() {
        const input = document.getElementById("arq-input");
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        addMessage("user", text);
        const typing = addMessage("bot", "...");

        try {
            const res = await fetch(`${BACKEND_URL}/chat`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ message: text, session_id: sessionId })
            });
            const data = await res.json();
            typing.remove();
            addMessage("bot", data.reply);
        } catch(e) {
            typing.remove();
            addMessage("bot", "Sorry, something went wrong. Please try again.");
        }
    }

    document.getElementById("arq-toggle").addEventListener("click", toggleChat);
    document.getElementById("arq-send").addEventListener("click", sendMessage);
    document.getElementById("arq-input").addEventListener("keypress", e => {
        if (e.key === "Enter") sendMessage();
    });
})();