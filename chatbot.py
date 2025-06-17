import streamlit as st
import requests

# Custom CSS untuk tampilan yang lebih profesional
st.markdown("""
    <style>
    /* Styling untuk background dan container utama */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
    }
    
    /* Styling untuk header */
    .header-container {
        background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Styling untuk pesan chat */
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Styling untuk pesan user */
    .chat-message.user {
        background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
        color: white;
        margin-left: 20%;
    }
    
    /* Styling untuk pesan assistant */
    .chat-message.assistant {
        background: white;
        color: #1a237e;
        margin-right: 20%;
        border: 1px solid #e0e0e0;
    }
    
    /* Styling untuk input chat */
    .stChatInput {
        border-radius: 25px;
        border: 2px solid #1a237e;
        padding: 1rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stChatInput:focus {
        border-color: #283593;
        box-shadow: 0 0 0 2px rgba(40, 53, 147, 0.2);
    }
    
    /* Styling untuk tombol kirim */
    .stButton button {
        background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
        color: white;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton button:hover {
        background: linear-gradient(90deg, #283593 0%, #1a237e 100%);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Styling untuk spinner loading */
    .stSpinner {
        color: #1a237e;
    }
    
    /* Styling untuk footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 0.9rem;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

#==============================================================#
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"

HEADERS = {
    "Authorization" : f"Bearer {OPENROUTER_API_KEY}",
    "Http-Referer" : "http://localhost:8501",
    "Content-Type" : "application/json",
    "X-title" : "AI Chatbot Streamlit"
}

API_URL = f"https://openrouter.ai/api/v1/chat/completions"
#==============================================================#

# Header yang lebih menarik
st.markdown("""
    <div class="header-container">
        <h1 style="color: white; text-align: center; margin-bottom: 0.5rem;">🤖 AI Assistant Pro</h1>
        <p style="color: #e0e0e0; text-align: center; font-size: 1.1rem;">Ditenagai oleh Mistral AI dan OpenRouter</p>
    </div>
""", unsafe_allow_html=True)

#chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Untuk menampilkan chat sebelumnya
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Input dari user
user_input = st.chat_input("Ketik pesan Anda di sini...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role" : "user", "content" : user_input})

    # Kirim ke API OpenRouter
    with st.spinner("🤔 Sedang memproses..."):
        payload = {
            "model" : MODEL,
            "messages" : [
                {"role" : "user", "content" : "You are a helpful assistant."},
                {"role" : "user", "content" : user_input}
            ]
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            bot_reply = response.json()["choices"][0]["message"]["content"]
        else:
            bot_reply = "⚠️ Maaf, terjadi kesalahan dalam memproses permintaan Anda."

    st.chat_message("assistant").markdown(bot_reply)
    st.session_state.chat_history.append({"role" : "assistant", "content" : bot_reply})

# Footer
st.markdown("""
    <div class="footer">
        Dibuat dengan ❤️ menggunakan Streamlit | AI Assistant Pro v1.0
    </div>
""", unsafe_allow_html=True)




