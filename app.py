"""
AI Personal Knowledge Assistant
Main Streamlit Application

A RAG-based document Q&A system powered by Google Gemini.
Upload PDFs/DOCX, ask questions, and get AI-powered answers.
"""

import os
import logging
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configure a clean, user-friendly logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler()]
)

# Silence noisy HTTP logs from third-party libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

from src.qa_chain import QAChain
from src.vector_store import VectorStore
from src.utils import (
    save_uploaded_file,
    get_file_type,
    generate_doc_id,
    format_file_size,
    ensure_directories,
    text_to_speech,
    cleanup_temp_files,
)


# ─── Page Configuration ──────────────────────────────────────────────
from PIL import Image

icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
page_icon = Image.open(icon_path) if os.path.exists(icon_path) else "🧠"

st.set_page_config(
    page_title=" SarvGyan",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme Toggle ─────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark = st.session_state.dark_mode

# ─── Custom CSS ───────────────────────────────────────────────────────
if dark:
    theme_css = """
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #4285F4, #34A853);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            color: #9AA0A6;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        .stChatMessage { border-radius: 12px; }
    </style>
    """
else:
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #FFFFFF;
            color: #1a1a1a;
        }
        [data-testid="stSidebar"] {
            background-color: #F0F2F6;
            color: #1a1a1a;
        }
        [data-testid="stHeader"] {
            background-color: #FFFFFF;
        }
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #1a73e8, #188038);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            color: #5F6368;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        .stChatMessage { border-radius: 12px; }
        p, span, label, div, h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a !important;
        }
        [data-testid="stChatInput"] textarea {
            color: #1a1a1a !important;
            background-color: #F0F2F6 !important;
        }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)


# ─── API Key Validation ───────────────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY", "")
if not api_key or api_key == "your_groq_api_key_here":
    st.error(
        "⚠️ **Groq API Key not configured!** "
        "Please set `GROQ_API_KEY` in your `.env` file. "
        "Get a free key at [console.groq.com/keys](https://console.groq.com/keys)."
    )
    st.stop()


# ─── Session State Initialization ─────────────────────────────────────
def init_session_state():
    """Initialize Streamlit session state variables."""
    if "qa_chain" not in st.session_state:
        ensure_directories()
        st.session_state.vector_store = VectorStore()
        st.session_state.qa_chain = QAChain(st.session_state.vector_store)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "indexed_docs" not in st.session_state:
        # Load existing documents from the database
        st.session_state.indexed_docs = st.session_state.vector_store.list_documents()


init_session_state()


# ─── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="main-header">🧠 SarvGyan</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your intelligent document assistant</p>', unsafe_allow_html=True)

    st.divider()

    # Document upload section
    st.subheader("📄 Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose PDF or DOCX files",
        type=["pdf", "docx", "doc"],
        accept_multiple_files=True,
        help="Upload one or more documents to index for Q&A.",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            doc_id = generate_doc_id(uploaded_file.name)

            if doc_id not in st.session_state.indexed_docs:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    logger.info(f"Processing document: {uploaded_file.name}")
                    try:
                        file_type = get_file_type(uploaded_file.name)
                        saved_path = save_uploaded_file(uploaded_file)

                        result = st.session_state.qa_chain.index_document(
                            file_path=saved_path,
                            file_type=file_type,
                            doc_id=doc_id,
                        )

                        st.session_state.indexed_docs.append(doc_id)
                        st.success(
                            f"✅ **{uploaded_file.name}** indexed "
                            f"({result['chunks_indexed']} chunks)"
                        )
                        logger.info(f"✨ [Complete]   Successfully indexed document: {uploaded_file.name}")
                    except Exception as e:
                        logger.error(f"❌ [Error]      Processing {uploaded_file.name}: {e}")
                        st.error(f"❌ Error processing {uploaded_file.name}: {e}")

    st.divider()

    # Indexed documents list
    st.subheader("📚 Indexed Documents")
    if st.session_state.indexed_docs:
        for doc_id in st.session_state.indexed_docs:
            st.markdown(f"• `{doc_id}`")

        total_chunks = st.session_state.vector_store.get_document_count()
        st.caption(f"Total chunks in database: {total_chunks}")
    else:
        st.info("No documents indexed yet. Upload files above to get started.")

    st.divider()

    # Actions
    st.subheader("⚙️ Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            logger.info("User cleared chat history")
            st.session_state.messages = []
            st.session_state.qa_chain.clear_history()
            st.rerun()

    with col2:
        if st.button("🔄 Reset All", use_container_width=True):
            logger.info("User requested full application reset")
            st.session_state.vector_store.reset()
            st.session_state.indexed_docs = []
            st.session_state.messages = []
            st.session_state.qa_chain.clear_history()
            cleanup_temp_files()
            logger.info("Application reset complete")
            st.rerun()


# ─── Main Chat Area ──────────────────────────────────────────────────
st.markdown('<p class="main-header">🧠 SarvGyan</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Ask questions about your uploaded documents</p>',
    unsafe_allow_html=True,
)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show sources if available
        if message.get("sources"):
            with st.expander("📎 Sources"):
                for source in message["sources"]:
                    st.caption(f"• {source}")

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Check if documents are indexed
    if not st.session_state.indexed_docs:
        st.warning("⚠️ Please upload and index documents first using the sidebar.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    logger.info(f"User asking question: {prompt}")
                    result = st.session_state.qa_chain.ask_question(prompt)

                    st.markdown(result["answer"])

                    # Show sources
                    if result["sources"]:
                        with st.expander("📎 Sources"):
                            for source in result["sources"]:
                                st.caption(f"• {source}")
                    
                    logger.info(f"✅ [Complete]   Generated response ({len(result['answer'])} chars) using {len(result['sources'])} sources\n")

                    # Store assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                    })

                except Exception as e:
                    error_msg = f"❌ Error generating response: {e}"
                    logger.error(f"Failed to generate response: {e}")
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                    })


# ─── Footer ───────────────────────────────────────────────────────────
st.divider()
st.caption("© 2025 SarvGyan. All rights reserved.")
