import streamlit as st
import requests
import json
import os
from datetime import datetime

# Hide Streamlit default menu
st.set_page_config(
    page_title="AI Assistant Pro",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for sidebar visibility
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

def toggle_sidebar():
    if st.session_state.sidebar_state == 'expanded':
        st.session_state.sidebar_state = 'collapsed'
    else:
        st.session_state.sidebar_state = 'expanded'

# Fungsi untuk menyimpan chat history ke file
def save_chat_history(chat_history):
    if not os.path.exists('chat_histories'):
        os.makedirs('chat_histories')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'chat_histories/chat_history_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'messages': chat_history
        }, f, ensure_ascii=False, indent=2)

# Fungsi untuk memuat semua sesi chat
def load_chat_sessions():
    sessions = []
    if os.path.exists('chat_histories'):
        for filename in os.listdir('chat_histories'):
            if filename.endswith('.json'):
                with open(f'chat_histories/{filename}', 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        # Ambil semua pertanyaan user dari sesi ini
                        questions = [(i, msg['content']) 
                                   for i, msg in enumerate(data['messages']) 
                                   if msg['role'] == 'user']
                        
                        # Buat entry untuk setiap pertanyaan
                        for q_idx, question in questions:
                            sessions.append({
                                'filename': filename,
                                'timestamp': data.get('timestamp', filename.split('_')[2].split('.')[0]),
                                'question': question,
                                'q_index': q_idx,  # Simpan index untuk load bagian spesifik
                                'total_questions': len(questions)
                            })
                    except:
                        continue
    return sorted(sessions, key=lambda x: (x['timestamp'], x['q_index']), reverse=True)

# Fungsi untuk memuat chat history spesifik
def load_specific_chat_history(filename, q_index):
    try:
        with open(f'chat_histories/{filename}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            messages = data.get('messages', [])
            # Ambil semua pesan sampai dengan pertanyaan yang dipilih dan jawaban berikutnya
            relevant_messages = []
            for i, msg in enumerate(messages):
                if i <= q_index + 1:  # Ambil sampai jawaban setelah pertanyaan yang dipilih
                    relevant_messages.append(msg)
            return relevant_messages
    except:
        return []

# Inisialisasi session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS untuk tampilan yang lebih profesional
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

div[data-testid="stToolbar"] {
    visibility: hidden;
}

.navbar-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: linear-gradient(135deg, #232526 0%, #414345 100%);
    z-index: 999999;
    padding: 0 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.navbar-title {
    display: flex;
    align-items: center;
    gap: 10px;
    color: white;
    font-size: 1.2rem;
    font-weight: bold;
    font-family: 'Press Start 2P', cursive;
    text-transform: uppercase;
    letter-spacing: 2px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    cursor: pointer;
    transition: all 0.3s ease;
}

.navbar-title:hover {
    transform: scale(1.05);
    color: #ff4b4b;
}

.navbar-menu {
    display: flex;
    gap: 20px;
}

.navbar-item {
    color: #e0e0e0;
    text-decoration: none;
    padding: 5px 15px;
    border-radius: 5px;
    transition: all 0.3s ease;
    font-size: 0.9rem;
    cursor: pointer;
}

.navbar-item:hover {
    background-color: rgba(255,255,255,0.1);
    color: white;
}

.main-content {
    margin-top: 60px;
    padding: 1rem;
}

.stApp {
    background: none;
}

/* Chat message styling */
.chat-message {
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    color: black;
}

.chat-message.user {
    background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
    color: black;
    margin-left: 20%;
    text-align: right;
    display: flex;
    flex-direction: row-reverse;
    justify-content: flex-end;
    align-items: center;
}

.chat-message.assistant {
    background: white;
    color: black !important;
    margin-right: 20%;
    border: 1px solid #e0e0e0;
    text-align: left;
}

/* Input styling */
.stChatInput {
    border-radius: 25px;
    border: 1px solidrgb(21, 20, 20);
    padding: 1rem;
    background: grey;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stChatInput:focus {
    border-color: #283593;
    box-shadow: 0 0 0 2px rgba(40,53,147,0.2);
}

/* Button styling */
.stButton button {
    background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
    color: white;
    border-radius: 25px;
    padding: 0.5rem 2rem;
    border: none;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stButton button:hover {
    background: linear-gradient(90deg, #283593 0%, #1a237e 100%);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Spinner styling */
.stSpinner {
    color: #1a237e;
}

/* Custom sidebar styling */
section[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(135deg, #232526 0%, #414345 100%);
    border-radius: 20px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    padding: 2rem 1rem 2rem 1rem;
    margin: 1.5rem 0.5rem 1.5rem 0.5rem;
    min-height: 90vh;
}

[data-testid="stSidebar"] {
    z-index: 999998;
    margin-top: 60px;
    background: linear-gradient(135deg, #232526 0%, #414345 100%);
}

.sidebar-trigger {
    position: fixed;
    top: 0;
    left: 0;
    width: 200px;
    height: 60px;
    z-index: 999999;
    cursor: pointer;
    background: transparent;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Render navbar with clickable title for sidebar toggle
st.markdown("""
    <div class="navbar-container">
        <div class="navbar-title" onclick="handleSidebarToggle()">
            🤖 CHATBOT
        </div>
        <div class="navbar-menu">
            <span class="navbar-item">Home</span>
            <span class="navbar-item">About</span>
            <span class="navbar-item">Settings</span>
        </div>
    </div>

    <script>
        function handleSidebarToggle() {
            window.parent.document.querySelector('button[kind=secondary][aria-label="Toggle sidebar"]').click();
        }
    </script>
""", unsafe_allow_html=True)

# Add spacing for navbar
st.markdown('<div style="margin-top: 60px;"></div>', unsafe_allow_html=True)

# Toggle sidebar based on state
if st.session_state.sidebar_state == 'expanded':
    st.sidebar.markdown("""
        <h1 style='color: white; text-align: left; margin-bottom: 0.5rem; font-size: 2rem;'>🤖 AI CHATBOT</h1>
        <p style='color: #cccccc; text-align: left; font-size: 1rem; margin-bottom: 1.5rem;'>Support by GPT and OpenRouter</p>
        <hr style='border: 1px solid #444;'>
        <h3 style='color: #ff4b4b; font-size: 1.1rem; margin-bottom: 0.5rem;'>Sesi Chat Sebelumnya</h3>
    """, unsafe_allow_html=True)


    
    # Load and display chat sessions in sidebar
    chat_sessions = load_chat_sessions()
    current_date = None

    for session in chat_sessions:
        timestamp = datetime.strptime(session['timestamp'], "%Y%m%d_%H%M%S")
        date_str = timestamp.strftime("%d/%m/%Y")
        
        # Tampilkan tanggal sebagai pemisah jika berbeda dari sebelumnya
        if date_str != current_date:
            st.sidebar.markdown(f"### 📅 {date_str}")
            current_date = date_str
        
        # Tampilkan waktu dan pertanyaan
        time_str = timestamp.strftime("%H:%M")
        question_preview = session['question'][:50] + "..." if len(session['question']) > 50 else session['question']
        
        if st.sidebar.button(
            f"📝 Pertanyaan: {question_preview}",
            key=f"{session['filename']}_{session['q_index']}",
            help=f"Waktu: {time_str}",
            use_container_width=True
        ):
            st.session_state.chat_history = load_specific_chat_history(session['filename'], session['q_index'])

    # Display current chat history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

#==============================================================#
OPENROUTER_API_KEY = st.text_input("input token disini")
MODEL = "openai/gpt-3.5-turbo"

HEADERS = {
    "Authorization" : f"Bearer {OPENROUTER_API_KEY}",
    "Http-Referer" : "http://localhost:8501",
    "Content-Type" : "application/json",
    "X-title" : "AI Chatbot Streamlit"
}

API_URL = f"https://openrouter.ai/api/v1/chat/completions"
#==============================================================#

# Chat input
user_input = st.chat_input("Ketik pesan Anda di sini...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Send to OpenRouter API
    with st.spinner("🤔 Processing..."):
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            bot_reply = response.json()["choices"][0]["message"]["content"]
        else:
            bot_reply = "⚠️ Maaf, terjadi kesalahan dalam memproses permintaan Anda."

    st.chat_message("assistant").markdown(bot_reply)
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    
    # Save chat history
    save_chat_history(st.session_state.chat_history)

# # Footer
# st.markdown("""
#     <div class="footer">
#         Dibuat dengan ❤️ menggunakan Streamlit | AI Assistant Pro v1.0
#     </div>
# """, unsafe_allow_html=True)