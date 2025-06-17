import streamlit as st
import requests

#==============================================================#
OPENROUTER_API_KEY = "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"
# MODEL = "mistralai/mistral-7b-instruct-v0.2"
MODEL = "openai/gpt-3.5-turbo"

HEADERS = {
    "Authorization" : f"Bearer {OPENROUTER_API_KEY}",
    "Http-Referer" : "http://localhost:8501",
    "Content-Type" : "application/json",
    "X-title" : "AI Chatbot Streamlit"
}

API_URL = f"https://openrouter.ai/api/v1/chat/completions"
#==============================================================#

st.title("CHATBOT with OpenRouter and Bubble Style🧠")
st.markdown(f"Powered by '[Mistral AI]' and 'OpenRouter'")

#chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Untuk menambilkan chat sebelumnya
for chat in st.session_state.chat_history : 
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Input dari user
user_input = st.chat_input("Type your message here...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role" : "user", "content" : user_input})

    # Kirim ke API OpenRouter
    with st.spinner("Thinking..."):
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
            bot_reply = "⚠️ Maaf gagal mendapatkan respon dari AI."

    st.chat_message("assistant").markdown(bot_reply)
    st.session_state.chat_history.append({"role" : "assistant", "content" : bot_reply})
