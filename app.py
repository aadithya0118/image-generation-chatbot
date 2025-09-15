# ui.py
import streamlit as st
from chatbot import (
    web_search_combined,
    ask_gemini_for_answer,
    generate_image_with_pollinations
)
import time

# ----------------------
# Page config
# ----------------------
st.set_page_config(
    page_title="Image generation chatbot 🤖",
    layout="wide"
)

# ----------------------
# Custom CSS
# ----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');
.stApp {background-color: #000000; font-family: 'Orbitron', sans-serif;}
.stSidebar {background-color: #ffffff;}
.stSidebar h2, .stSidebar p, .stSidebar label {color: #000000;}
.user-text {color: #fff;}
.bot-text {color: #BFFF00;}
.stTextInput>div>div>input {background-color: #222; color: #fff;}
.stButton>button {background-color: #0A0A0A; color: #BFFF00;}
</style>
""", unsafe_allow_html=True)

st.title("Image generation chatbot 🤖")

# ----------------------
# Icons
# ----------------------
USER_ICON = "https://www.pngall.com/wp-content/uploads/12/Wall-E-PNG-Clipart.png"
BOT_ICON = "https://icons.iconarchive.com/icons/noctuline/wall-e/128/EVE-icon.png"
THINKING_ICON = BOT_ICON  # EVE for thinking

# ----------------------
# Session state
# ----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------
# Sidebar
# ----------------------
st.sidebar.header("⚙️ Configuration")
enable_web_search = st.sidebar.checkbox("Enable web search", value=True)
generate_images = st.sidebar.checkbox("Auto-generate images", value=True)
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []

st.markdown("---")

# ----------------------
# Display chat
# ----------------------
for msg in st.session_state.messages:
    icon = USER_ICON if msg["role"] == "user" else BOT_ICON
    color = "#fff" if msg["role"] == "user" else "#BFFF00"
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(f"<div style='color:{color};'>{msg['content']}</div>", unsafe_allow_html=True)
        if msg.get("image"):
            st.image(msg["image"], caption="Generated Image", use_container_width=True)

# ----------------------
# User input
# ----------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show user message immediately
    with st.chat_message("user", avatar=USER_ICON):
        st.markdown(f"<div style='color:#fff;'>{user_input}</div>", unsafe_allow_html=True)

    # ----------------------
    # Show EVE thinking
    # ----------------------
    thinking_placeholder = st.empty()
    with thinking_placeholder.container():
        with st.chat_message("assistant", avatar=THINKING_ICON):
            st.markdown(f"<div style='color:#BFFF00;'>🤔 Imagine is thinking...</div>", unsafe_allow_html=True)

    # ----------------------
    # Generate response
    # ----------------------
    context = web_search_combined(user_input) if enable_web_search else "No web search used."
    raw_answer, image_prompt = ask_gemini_for_answer(user_input, context)

    # Filter out policy messages
    lines = raw_answer.split("\n")
    answer_lines = [line for line in lines if "This query does not violate the policy" not in line]
    answer = "\n".join(answer_lines).strip()

    # Generate image if requested
    image_bytes = None
    if image_prompt and generate_images:
        with st.spinner("🎨 Creating image..."):
            image_bytes = generate_image_with_pollinations(image_prompt)

    # ----------------------
    # Replace thinking with actual response
    # ----------------------
    thinking_placeholder.empty()  # Remove thinking message

    # Add assistant message and display it
    msg = {"role": "assistant", "content": answer}
    if image_bytes:
        msg["image"] = image_bytes
    st.session_state.messages.append(msg)

    with st.chat_message("assistant", avatar=BOT_ICON):
        st.markdown(f"<div style='color:#BFFF00;'>{answer}</div>", unsafe_allow_html=True)
        if image_bytes:
            st.image(image_bytes, caption="Generated Image", use_container_width=True)
try:
    answer, image_prompt = ask_gemini_for_answer(user_input, context)
except Exception as e:
    answer = "⚠️ Sorry! The API quota has been exceeded for today. Please try again tomorrow."
    image_prompt = None


