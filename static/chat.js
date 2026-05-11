const listings = [
        { id:1, address:"123 Oak Street, Austin, TX", price:450000, bed:3, bath:2, sqft:1850, emoji:"🏡", desc:"Charming single-family home in quiet neighborhood. Updated kitchen, hardwood floors, large backyard." },
        { id:2, address:"456 Maple Ave, Austin, TX", price:625000, bed:4, bath:3, sqft:2400, emoji:"🏘️", desc:"Modern home with open floor plan. Chef's kitchen, master suite with walk-in closet, 2-car garage." },
        { id:3, address:"789 Pine Road, Austin, TX", price:320000, bed:2, bath:1, sqft:1200, emoji:"🏠", desc:"Cozy starter home. Recently renovated bathroom, new roof 2023, energy-efficient windows." },
        { id:4, address:"321 Elm Boulevard, Austin, TX", price:890000, bed:5, bath:4, sqft:3600, emoji:"🏰", desc:"Luxury property with pool, home office, gourmet kitchen, smart home system." },
        { id:5, address:"654 Cedar Lane, Austin, TX", price:510000, bed:3, bath:2, sqft:2100, emoji:"🏡", desc:"Stunning renovated home. New kitchen with quartz countertops, spa-like master bath." }
    ];

    const grid = document.getElementById("listings-grid");
    listings.forEach(l => {
        grid.innerHTML += `
        <div class="card">
            <div class="card-img" style="background:hsl(${l.id*40+180},25%,90%)">${l.emoji}</div>
            <div class="card-body">
                <div class="card-price">$${l.price.toLocaleString()}</div>
                <div class="card-address">📍 ${l.address}</div>
                <div class="card-details">🛏 ${l.bed} bed · 🚿 ${l.bath} bath · 📐 ${l.sqft.toLocaleString()} sqft</div>
                <div class="card-desc">${l.desc}</div>
                <button class="card-btn" onclick="askAbout('${l.address}')">Ask AI About This Property</button>
            </div>
        </div>`;
    });

    // Session persistence
    let sessionId = localStorage.getItem('chat_session_id');
    if (!sessionId) {
        sessionId = Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chat_session_id', sessionId);
    }

    const savedMessages = JSON.parse(localStorage.getItem('chat_messages') || '[]');
    let chatOpen = false;

    function toggleChat() {
        chatOpen = !chatOpen;
        const win = document.getElementById("chat-window");
        win.classList.toggle("open", chatOpen);
        if (chatOpen) {
            if (savedMessages.length > 0) {
                document.getElementById("welcome-screen").style.display = "none";
                document.getElementById("chat-area").style.display = "flex";
                if (document.getElementById("chat-messages").children.length === 0) {
                    savedMessages.forEach(m => addMessage(m.role, m.text, true));
                }
            } else {
                document.getElementById("welcome-screen").style.display = "flex";
                document.getElementById("chat-area").style.display = "none";
            }
        }
    }

    function openChat() {
        if (!chatOpen) toggleChat();
    }

    function selectDept(dept) {
        document.getElementById("welcome-screen").style.display = "none";
        document.getElementById("chat-area").style.display = "flex";
        if (savedMessages.length === 0) {
            setTimeout(() => addMessage("bot", "Hi! 👋 I'm your Austin Realty assistant. How can I help you today?"), 300);
        }
        document.getElementById("chat-input").focus();
    }

    function askAbout(address) {
        openChat();
        document.getElementById("welcome-screen").style.display = "none";
        document.getElementById("chat-area").style.display = "flex";
        setTimeout(() => {
            document.getElementById("chat-input").value = `Tell me more about ${address}`;
            sendMessage();
        }, 300);
    }

    function getTime() {
        const now = new Date();
        return now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
    }

    function addMessage(role, text, skipSave = false) {
        const msgs = document.getElementById("chat-messages");
        const row = document.createElement("div");
        row.className = `msg-row ${role}`;

        const avatar = document.createElement("div");
        avatar.className = `msg-avatar ${role === 'user' ? 'user-av' : ''}`;
        avatar.textContent = role === 'bot' ? '🏠' : '👤';

        const bubble = document.createElement("div");
        bubble.className = "msg-bubble";

        const msg = document.createElement("div");
        msg.className = `msg ${role}`;
        if (role === "bot") {
            msg.innerHTML = text
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                .replace(/\n/g, "<br>");
        } else {
            msg.textContent = text;
        }

        const time = document.createElement("div");
        time.className = "msg-time";
        time.textContent = getTime();

        bubble.appendChild(msg);
        bubble.appendChild(time);
        row.appendChild(avatar);
        row.appendChild(bubble);
        msgs.appendChild(row);
        msgs.scrollTop = msgs.scrollHeight;

        if (!skipSave) {
            savedMessages.push({ role, text });
            localStorage.setItem('chat_messages', JSON.stringify(savedMessages));
        }

        return row;
    }

    function addTyping() {
        const msgs = document.getElementById("chat-messages");
        const row = document.createElement("div");
        row.className = "msg-row bot";
        row.id = "typing-row";

        const avatar = document.createElement("div");
        avatar.className = "msg-avatar";
        avatar.textContent = "🏠";

        const indicator = document.createElement("div");
        indicator.className = "typing-indicator";
        indicator.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;

        row.appendChild(avatar);
        row.appendChild(indicator);
        msgs.appendChild(row);
        msgs.scrollTop = msgs.scrollHeight;
        return row;
    }

    async function sendMessage() {
        const input = document.getElementById("chat-input");
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        addMessage("user", text);
        const typing = addTyping();

        try {
            const res = await fetch("/chat", {
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

    document.getElementById("chat-input").addEventListener("keypress", e => {
        if (e.key === "Enter") sendMessage();
    });