import streamlit as st
import requests
import json

# ========== CONFIGURATION ==========
# API_KEY = st.secrets["API_KEY"]  # Store this securely in .streamlit/secrets.toml
# API_KEY='sk-bedcb944ad3d4bae9b9dfa4080af75ce'
API_URL = "https://api.deepseek.com/v1/chat/completions"

# ========== SESSION STATE ==========
if "system_message" not in st.session_state:
    st.session_state.system_message = {
        "role": "system",
        "content": (
            "You are a respectful, insightful travel assistant helping Professor Sundararajan navigate his 3-day academic trip to Bogota. "
            "You provide elegant answers about itinerary items, meetings, transport, cultural visits, and fine dining. "
            "Given that Professor Sundararajan is likely occupied with academic engagements throughout most of the day, with only a few discretionary hours in the evening, "
            "your responsibility is not to enumerate all possible activities, but to curate only those experiences that offer high cultural or gastronomic value "
            "commensurate with the constraints on his time. Your recommendations should reflect careful prioritization—highlighting singular destinations or experiences "
            "each evening that justify the limited time investment and avoid decision fatigue. Optimize for insight, efficiency, and experiential return."
        )
    }

# ========== SIDEBAR ==========
with st.sidebar:
    st.subheader("🧭 Assistant Guide")
    st.markdown(
        """
        - Ask about **agenda for a specific day**
        - Inquire about **fine dining** or **logistics**
        - Ask for **evening cultural experiences**
        - Indicate **time or dietary constraints**
        """
    )
    st.info("Built with DeepSeek API & Streamlit")

# ========== APP HEADER ==========
st.title("Professor Sundararajan's Bogotá Itinerary Assistant")
st.markdown("Ask about your curated academic visit — including sessions, dining, and select cultural experiences.")

# ========== CHAT FORM ==========
with st.form("chat_form"):
    user_input = st.text_input("Your question:", placeholder="e.g., What’s planned for Day 2 evening?")
    submitted = st.form_submit_button("Ask")

# ========== STREAMING RESPONSE HANDLER ==========
def stream_deepseek_response(prompt):
    messages = [
        st.session_state.system_message,
        {"role": "user", "content": prompt}
    ]
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "temperature": 0.5,
            "stream": True,
            "messages": messages
        },
        stream=True,
    )

    full_reply = ""
    for line in response.iter_lines():
        if line:
            try:
                line_str = line.decode("utf-8").replace("data: ", "")
                if line_str.strip() == "[DONE]":
                    break
                parsed = json.loads(line_str)
                delta = parsed["choices"][0]["delta"].get("content", "")
                full_reply += delta
                yield delta
            except Exception as e:
                yield f"\n[Error parsing stream: {str(e)}]"

    st.session_state.last_user_message = prompt
    st.session_state.last_assistant_reply = full_reply

# ========== RESPONSE DISPLAY ==========
if submitted and user_input:
    with st.spinner("Consulting the itinerary assistant..."):
        st.markdown("---")
        st.subheader("🧑‍🏫 Professor Sundararajan:")
        st.markdown(user_input)

        st.subheader("🤖 Assistant:")
        reply_placeholder = st.empty()

        full_text = ""
        for chunk in stream_deepseek_response(user_input):
            full_text += chunk
            reply_placeholder.markdown(full_text)
