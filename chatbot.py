import streamlit as st
import requests
import json
import os
from datetime import datetime

# Hide Streamlit default menu
st.set_page_config(
    page_title="ChatBot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Custom CSS untuk tampilan yang lebih profesional
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

button[data-testid="stSidebarNavCollapseButton"],
button[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

div[data-testid="stToolbar"] {
    visibility: hidden;
}

.main-content {
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
    color: white;
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

/* Input styling for responsiveness */
div[data-testid="stChatInput"] {
    background-color: transparent !important;
    border-top: none !important;
    padding-bottom: 1rem; /* Space for the floating input */
}

/* The actual floating input box */
div[data-testid="stChatInput"] > div {
    border-radius: 25px;
    border: 1px solid #4f4f6a;
    padding: 0.5rem 1rem;
    background: #2d2d44;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    transition: all 0.2s ease-in-out;
}

div[data-testid="stChatInput"] > div:focus-within {
    border-color: #6366f1;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

/* The actual text input field inside */
div[data-testid="stChatInput"] input {
    background-color: transparent !important;
    border: none !important;
    color: white;
    padding: 0 !important;
}

div[data-testid="stChatInput"] input::placeholder {
    color: #a0a0b0 !important;
    font-style: italic;
}

/* Send button styling */
button[data-testid="stChatMessageSendButton"] svg {
    fill: white;
    transition: fill 0.2s ease-in-out;
}

button[data-testid="stChatMessageSendButton"]:hover svg {
    fill: #6366f1;
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
    background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
    border-radius: 0 20px 20px 0;
    box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    padding: 1rem;
    margin: 1rem 0 1rem 0;
    min-height: 90vh;
    border-left: 3px solid #6366f1;
}

[data-testid="stSidebar"] {
    z-index: 999998;
    background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
}

/* Sidebar content styling */
[data-testid="stSidebar"] .stMarkdown {
    color: #e2e8f0;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
    font-weight: 600;
}

[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    color: white;
    padding: 0.75rem;
}

/* Sidebar button styling */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Success and warning message styling */
[data-testid="stSidebar"] .stAlert {
    border-radius: 8px;
    border: none;
    padding: 0.75rem;
    margin: 0.5rem 0;
}

[data-testid="stSidebar"] .stAlert[data-baseweb="notification"] {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
    border-left: 4px solid #22c55e;
}

[data-testid="stSidebar"] .stAlert[data-baseweb="notification"][data-testid="stAlert"] {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
    border-left: 4px solid #f59e0b;
}

/* Info message styling */
[data-testid="stSidebar"] .stAlert[data-baseweb="notification"][data-testid="stAlert"] {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    border-left: 4px solid #3b82f6;
}

/* Divider styling */
[data-testid="stSidebar"] hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    margin: 1.5rem 0;
}

/* Small text styling */
[data-testid="stSidebar"] small {
    color: #94a3b8;
    font-size: 0.75rem;
}

/* Footer styling */
[data-testid="stSidebar"] .stMarkdown p {
    margin: 0.25rem 0;
    color: #64748b;
}
</style>
""", unsafe_allow_html=True)

# Inisialisasi awal agar variabel selalu ada
OPENROUTER_API_KEY = ""

# Render sidebar
with st.sidebar:
    # Header section with better styling
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 2px solid #444; margin-bottom: 2rem;">
            <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: bold;'>🤖 AI CHATBOT</h1>
            <p style='color: #cccccc; margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Powered by OpenAI GPT-3.5 & OpenRouter</p>
        </div>
    """, unsafe_allow_html=True)
    
    # API Key section with better organization
    st.markdown("### 🔑 API Configuration")
    OPENROUTER_API_KEY = st.text_input(
        "OpenRouter API Key", 
        type="password",
        placeholder="Enter your API key here...",
        help="Get your API key from https://openrouter.ai/keys"
    )
    
    # API Key status indicator
    if OPENROUTER_API_KEY:
        st.success("✅ API Key configured successfully")
    else:
        st.warning("⚠️ Please enter your API Key to start chatting")
    
    st.write("""
    Perhatikan : 
    - API Key harus diisi untuk memulai chat
    - API Key dapat diambil di https://openrouter.ai/keys
    - Selain dari OpenRouter, API Key lainnya tidak dapat digunakan
    """)

    st.markdown("---")
    
    # Chat History section with better organization
    st.markdown("### 📚 Chat History")
    
    # Load and display chat sessions
    chat_sessions = load_chat_sessions()
    
    if not chat_sessions:
        st.info("No chat history found. Start a new conversation!")
    else:
        current_date = None
        for session in chat_sessions:
            session_id = f"{session['filename']}_{session['q_index']}"
            timestamp = datetime.strptime(session['timestamp'], "%Y%m%d_%H%M%S")
            date_str = timestamp.strftime("%d/%m/%Y")
            
            # Date header
            if date_str != current_date:
                st.markdown(f"**📅 {date_str}**")
                current_date = date_str
            
            # Time and question preview
            time_str = timestamp.strftime("%H:%M")
            question_preview = session['question'][:40] + "..." if len(session['question']) > 40 else session['question']
            
            # Create a more compact button layout
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                if st.button(
                    f"💬 {question_preview}",
                    key=f"btn_{session_id}",
                    use_container_width=True
                ):
                    st.session_state.chat_history = load_specific_chat_history(session['filename'], session['q_index'])
                    st.session_state.current_chat_id = session_id
                    st.rerun()
            
            with col2:
                st.markdown(f"<div style='text-align: right; padding-top: 0.5rem;'><small style='color: #888;'>{time_str}</small></div>", unsafe_allow_html=True)
            
            # Add small spacing between items
            st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer section
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0; color: #888; font-size: 0.8rem;">
            <p>Created By Josias Marchellino Pakpahan</p>
            <p>Version 1.0</p>
        </div>
    """, unsafe_allow_html=True)

#==============================================================#
# MODEL dan API URL
MODEL = "openai/gpt-3.5-turbo"

HEADERS = {
    "Authorization" : f"Bearer {OPENROUTER_API_KEY}",
    "Http-Referer" : "http://localhost:8501",
    "Content-Type" : "application/json",
    "X-title" : "AI Chatbot Streamlit"
}

API_URL = f"https://openrouter.ai/api/v1/chat/completions"
#==============================================================#

# Display chat messages from history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")


if user_input:
    # If starting a new chat after viewing history, reset history
    if st.session_state.current_chat_id is not None:
        st.session_state.chat_history = []
        st.session_state.current_chat_id = None

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
    
    st.rerun()