import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from chat_manager import initialize_chat, delete_chat
from chat_storage import save_chats

# RAG modules
from rag.pdf_processor import process_pdf
from rag.embeddings import create_embeddings
from rag.retriever import create_vector_store, create_retriever

# LOAD ENVIRONMENT VARIABLES

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# INITIALIZE CHAT

initialize_chat()

# INITIALIZE RAG STATE


if "vector_store" not in st.session_state:

    st.session_state.vector_store = None

if "processed_files" not in st.session_state:

    st.session_state.processed_files = []
# SIDEBAR

st.sidebar.title("💬 Chat History")

# PDF UPLOAD


st.sidebar.subheader("📄 Upload Documents")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# GET CURRENT FILE NAMES

current_files = [
    file.name
    for file in uploaded_files
]

# PROCESS PDFs

if (
    uploaded_files
    and current_files != st.session_state.processed_files
):

    st.sidebar.info(
        "⏳ Processing uploaded documents..."
    )


    # Store all documents from all PDFs

    all_documents = []

    # PROCESS EACH PDF

    for uploaded_file in uploaded_files:

        documents = process_pdf(
            uploaded_file
        )

        all_documents.extend(
            documents
        )

        st.sidebar.success(
            f"✅ {uploaded_file.name} loaded"
        )

        st.sidebar.info(
            f"📄 {uploaded_file.name}: "
            f"{len(documents)} chunks"
        )

    # CREATE EMBEDDINGS

    embeddings = create_embeddings()

   # CREATE FAISS VECTOR STORE

    st.session_state.vector_store = (

        create_vector_store(
            all_documents,
            embeddings
        )
    )

    # SAVE PROCESSED FILE NAMES


    st.session_state.processed_files = (
        current_files
    )

    st.sidebar.success(
        f"✅ {len(all_documents)} total chunks embedded"
    )

    st.sidebar.success(
        "✅ FAISS vector store created!"
    )

# DOCUMENT STATUS

elif (
    uploaded_files
    and st.session_state.vector_store
):

    st.sidebar.success(
        "✅ Documents ready"
    )

# NEW CHAT BUTTON

if st.sidebar.button(
    "➕ New Chat"
):

    new_chat = (
        f"Chat {len(st.session_state.chats) + 1}"
    )

    st.session_state.chats[new_chat] = []

    st.session_state.current_chat = (
        new_chat
    )

    st.rerun()

# DISPLAY CHAT HISTORY

for chat_name in list(
    st.session_state.chats.keys()
):


    col1, col2 = st.sidebar.columns(
        [4, 1]
    )

    # OPEN CHAT

    with col1:

        if st.button(
            chat_name,
            key=chat_name
        ):

            st.session_state.current_chat = (
                chat_name
            )

            st.rerun()

    # DELETE CHAT

    with col2:

        if st.button(
            "🗑",
            key=f"delete_{chat_name}"
        ):

            delete_chat(
                chat_name
            )


            save_chats(
                st.session_state.chats
            )


            st.rerun()

# MAIN SCREEN

st.title(
    "🤖 SMART AI Assistant"
)

# CURRENT CHAT

messages = st.session_state.chats[
    st.session_state.current_chat
]

# DISPLAY PREVIOUS MESSAGES

for message in messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

# CHAT INPUT

question = st.chat_input(
    "Ask anything..."
)

# PROCESS QUESTION

if question:

    current_chat = (
        st.session_state.current_chat
    )

    # AUTOMATIC CHAT TITLE

    if (

        current_chat.startswith("Chat")

        and len(messages) == 0

    ):

        title = question[:30]

        st.session_state.chats[title] = (

            st.session_state.chats.pop(
                current_chat
            )

        )

        st.session_state.current_chat = (
            title
        )

        messages = (
            st.session_state.chats[
                title
            ]
        )

        save_chats(
            st.session_state.chats
        )

    # SAVE USER MESSAGE

    messages.append(

        {
            "role": "user",
            "content": question
        }

    )

    save_chats(
        st.session_state.chats
    )

    # DISPLAY USER MESSAGE

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    # RAG + GROQ

    try:

        # PDF / RAG MODE

        if (

            uploaded_files

            and st.session_state.vector_store

        ):

            # CREATE RETRIEVER

            retriever = create_retriever(

                st.session_state.vector_store,

                k=3
            )

            # RETRIEVE RELEVANT DOCUMENTS

            retrieved_docs = (

                retriever.invoke(
                    question
                )
            )

            # CREATE PDF CONTEXT

            context = "\n\n".join(

                doc.page_content

                for doc in retrieved_docs
            )

            # CREATE CONVERSATION HISTORY

            conversation_history = "\n".join(

                f"{message['role'].upper()}: "
                f"{message['content']}"

                for message in messages[:-1]

            )

            # RAG PROMPT

            rag_prompt = f"""

You are a helpful conversational AI assistant.

Use the uploaded PDF information and the
conversation history to answer the user's
current question.

IMPORTANT RULES:

1. Use the PDF information when the question
   is related to the uploaded documents.

2. Use the conversation history to understand
   follow-up questions.

3. If the requested information is not available
   in the uploaded documents, clearly say:

"The information is not available
in the uploaded documents."

4. Do not invent facts.

5. Give a clear and concise answer.

CONVERSATION HISTORY:

{conversation_history}


PDF INFORMATION:

{context}


CURRENT USER QUESTION:

{question}

"""
            # CREATE RAG MESSAGES

            rag_messages = (

                messages[:-1]

                +

                [
                    {
                        "role": "user",
                        "content": rag_prompt
                    }
                ]

            )

        # NORMAL CHAT MODE

        else:


            rag_messages = messages


            retrieved_docs = []

        # CALL GROQ API

        response = (

            client.chat.completions.create(

                model="openai/gpt-oss-120b",

                messages=rag_messages

            )
        )

        # GET AI ANSWER

        answer = (

            response
            .choices[0]
            .message
            .content
        )

    # ERROR HANDLING

    except Exception as e:

        st.error(
            "⚠️ Groq Error"
        )

        st.exception(e)

        answer = None

        retrieved_docs = []

    # SAVE + DISPLAY ANSWER

    if answer:

        messages.append(

            {
                "role": "assistant",
                "content": answer
            }

        )

        save_chats(
            st.session_state.chats
        )

        # DISPLAY AI RESPONSE

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                answer
            )

            # DISPLAY SOURCES

            if retrieved_docs:

                st.markdown(
                    "### 📚 Sources"
                )

                displayed_sources = set()

                for doc in retrieved_docs:

                    source = doc.metadata.get(

                        "source",

                        "Unknown document"
                    )

                    page = doc.metadata.get(

                        "page",

                        "Unknown page"
                    )

                    source_key = (

                        source,

                        page
                    )

                    # REMOVE DUPLICATE SOURCES

                    if (
                        source_key
                        not in displayed_sources
                    ):

                        st.markdown(

                            f"📄 **{source}** — "
                            f"Page **{page}**"
                        )

                        displayed_sources.add(
                            source_key
                        )