import streamlit as st
import requests

# ========== CONFIGURATION ==========
API_KEY = "sk-bedcb944ad3d4bae9b9dfa4080af75ce"
API_URL = "https://api.deepseek.com/v1/chat/completions"

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
               "You are a respectful, insightful travel assistant helping Professor Arun navigate his 3-day academic trip to Bogota. "
                "You provide elegant answers about itinerary items, meetings, transport, cultural visits, and fine dining. "
                "Given that Professor Arun is likely occupied with academic engagements throughout most of the day, with only a few discretionary hours in the evening, "
                "your responsibility is not to enumerate all possible activities, but to curate only those experiences that offer high cultural or gastronomic value "
                "commensurate with the constraints on his time. Your recommendations should reflect careful prioritization—highlighting singular destinations or experiences "
                "each evening that justify the limited time investment and avoid decision fatigue. Optimize for insight, efficiency, and experiential return."
            )
        }
    ]

# ========== APP HEADER ==========
st.title("Professor Arun's Bogota Itinerary Assistant")
st.markdown("Ask any questions about your visit — academic sessions, cultural highlights, fine dining, and more.")

# ========== USER INPUT ==========
user_input = st.text_input("Your question:", placeholder="e.g., What's on the agenda for Day 2 evening?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "temperature": 0.5,
            "messages": st.session_state.messages
        }
    )

    if response.status_code == 200:
        assistant_reply = response.json()["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    else:
        st.error(f"API Error: {response.status_code}")
        assistant_reply = ""

# ========== CHAT HISTORY ==========
for msg in st.session_state.messages[1:]:  # Skip system message
    if msg["role"] == "user":
        st.markdown(f"**Professor Arun:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")
