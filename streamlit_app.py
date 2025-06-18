import streamlit as st
import requests
import json

st.title("Credit Card Recommender")

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = 'user_' + str(hash(st))
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = None

# Function to start conversation
def start_conversation():
    response = requests.post('http://localhost:5000/api/start_conversation', 
                           json={'session_id': st.session_state.session_id})
    data = response.json()
    st.session_state.current_question = data['response']
    st.session_state.conversation.append(('Bot', data['response']))

# Function to submit answer
def submit_answer(answer):
    response = requests.post('http://localhost:5000/api/answer', 
                           json={'session_id': st.session_state.session_id, 'answer': answer})
    data = response.json()
    st.session_state.conversation.append(('User', answer))
    st.session_state.conversation.append(('Bot', data['response']))
    st.session_state.current_question = data['response']
    if data.get('recommendations'):
        st.session_state.recommendations = data['recommendations']
        st.session_state.show_recommendations = True

# Display conversation
for speaker, message in st.session_state.conversation:
    if speaker == 'Bot':
        st.write(f"🤖: {message}")
    else:
        st.write(f"👤: {message}")

# Input form
if not hasattr(st.session_state, 'show_recommendations') or not st.session_state.show_recommendations:
    if st.session_state.current_question is None:
        start_conversation()
    else:
        answer = st.text_input(st.session_state.current_question)
        if st.button("Submit"):
            submit_answer(answer)

# Show recommendations
if hasattr(st.session_state, 'show_recommendations') and st.session_state.show_recommendations:
    st.subheader("Recommended Credit Cards")
    for card in st.session_state.recommendations:
        st.write(f"**{card['name']}**")
        st.write(f"Issuer: {card['issuer']}")
        st.write(f"Reasons: {card['reasons']}")
        st.write(f"Estimated Rewards: {card['rewards_simulation']}")
        st.write("---")
    if st.button("Restart"):
        st.session_state.conversation = []
        st.session_state.current_question = None
        st.session_state.show_recommendations = False
        start_conversation()