import streamlit as st
from chat_storage import load_chats


def initialize_chat():

    # Load all chats from JSON file
    if "chats" not in st.session_state:

        chats = load_chats()

        if chats:
            st.session_state.chats = chats
        else:
            st.session_state.chats = {
                "Chat 1": []
            }

    # Set the current active chat
    if "current_chat" not in st.session_state:

        first_chat = list(st.session_state.chats.keys())[0]

        st.session_state.current_chat = first_chat


def delete_chat(chat_name):

    # Don't allow deleting the last chat
    if len(st.session_state.chats) == 1:
        return

    # Delete selected chat
    del st.session_state.chats[chat_name]

    # Open the first remaining chat
    first_chat = list(st.session_state.chats.keys())[0]

    st.session_state.current_chat = first_chat