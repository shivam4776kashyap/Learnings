import streamlit as st
import requests

# =========================
# Config
# =========================
OLLAMA_API = "http://localhost:11434/api/generate"
AVAILABLE_MODELS = ["mistral:7b", "starcoder2:3b"]

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Local ChatGPT UI", layout="wide")
st.title("💻 Local ChatGPT-like Assistant")

# Sidebar model selector
selected_model = st.sidebar.selectbox(
    "Choose a model:",
    AVAILABLE_MODELS,
    index=0
)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []  # full chat history
if "current_model" not in st.session_state:
    st.session_state.current_model = selected_model

# =========================
# Handle Model Switching
# =========================
if selected_model != st.session_state.current_model:
    st.session_state.current_model = selected_model

# =========================
# Display Chat History
# =========================
for role, text in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(text)

# =========================
# Build conversation context
# =========================
def build_context(messages):
    conversation = ""
    for role, msg in messages:
        if role == "user":
            conversation += f"User: {msg}\n"
        else:
            conversation += f"Assistant: {msg}\n"
    return conversation

# =========================
# User Input
# =========================
if prompt := st.chat_input("Type your message..."):
    # Add user input to chat history
    st.session_state.messages.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build full conversation context
    conversation_context = build_context(st.session_state.messages)

    # Send request to Ollama API with full history
    response = requests.post(
        OLLAMA_API,
        json={
            "model": st.session_state.current_model,
            "prompt": conversation_context,
            "stream": False
        }
    )

    if response.status_code == 200:
        result = response.json().get("response", "")
    else:
        result = f"⚠️ Error: {response.text}"

    # Add assistant response to history
    st.session_state.messages.append(("assistant", result))
    with st.chat_message("assistant"):
        st.markdown(result)

# =========================
# Clear history button
# =========================
if st.sidebar.button("🧹 Clear Conversation"):
    st.session_state.messages = []
