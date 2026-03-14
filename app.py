import streamlit as st
import requests
import uuid

API = "http://localhost:8000/chat"

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state["messages"] = []
# else:
#     st.write("Session Key does not exist")

st.title("Not so Netflix")

st.set_page_config(
    page_title="Not so Netflix",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you like to watch?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    payload = {
        "question": f"{prompt}",
        "session_id": st.session_state.session_id
    }
    try:
        with st.spinner("Thinking..."):
            response = requests.post(API, json=payload)
            response.raise_for_status()
            data = response.json()
            ai_reply = data["response"]
        with st.chat_message("assistant"):
            st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    except Exception as e:
        st.error(f"Error: {e}")

with st.sidebar:
    # st.markdown("Chat prompt ideas:\n" \
    # "Recommend me some movies.\n" \
    # "I liked this `name_of_the_movie`. Recommend me some movies.\n" \
    # "What is in my cart.?\n" \
    # "Add `name_of_the_movie` to the cart.\n" \
    # "Checkout my cart.")
    st.header("Chat Ideas")
    st.markdown("""
    - *"Recommend me some movies"*
    - *"I liked The Godfather. Recommend similar movies"*
    - *"Add The Godfather to my cart"*
    - *"What's in my cart?"*
    - *"Checkout"*
    """)
    if st.button("Reset", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()