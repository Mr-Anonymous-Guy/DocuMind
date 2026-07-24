"""
main.py - Entry point for DocuMind Streamlit UI.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import json
from src.storage.database import init_db, SessionLocal
from src.storage.faiss_manager import FaissManager
from src.ai.llm_manager import LLMManager
from src.ai.embed_manager import EmbedManager
from src.retrieval.rag_engine import RAGEngine
from src.services.collection_service import CollectionService
from src.services.document_service import DocumentService
from src.services.chat_service import ChatService
from src.services.productivity_service import ProductivityService

# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------
st.set_page_config(page_title="DocuMind AI", page_icon="🧠", layout="wide")

@st.cache_resource
def setup_dependencies():
    init_db()
    db = SessionLocal()
    embed_mgr = EmbedManager()
    llm_mgr = LLMManager()
    faiss_mgr = FaissManager(embed_mgr.get_embeddings())
    rag_engine = RAGEngine(llm_mgr, faiss_mgr)
    
    return {
        "db": db,
        "collection_service": CollectionService(db, faiss_mgr),
        "document_service": DocumentService(db, faiss_mgr),
        "chat_service": ChatService(db, rag_engine),
        "productivity_service": ProductivityService(llm_mgr, faiss_mgr)
    }

deps = setup_dependencies()

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# -----------------------------------------------------------------------------
# Session State
# -----------------------------------------------------------------------------
if 'current_collection_id' not in st.session_state:
    st.session_state.current_collection_id = None
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

# -----------------------------------------------------------------------------
# Sidebar Navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🧠 DocuMind")
    st.markdown("Your AI Knowledge Base")
    st.divider()
    
    st.subheader("📁 Workspaces")
    collections = deps["collection_service"].get_collections()
    
    # Create New Collection
    with st.expander("➕ New Collection", expanded=False):
        new_coll_name = st.text_input("Name")
        new_coll_desc = st.text_input("Description")
        if st.button("Create", use_container_width=True):
            if new_coll_name:
                deps["collection_service"].create_collection(new_coll_name, new_coll_desc)
                st.rerun()
                
    # List Collections
    for coll in collections:
        if st.button(f"{coll.name}", key=f"coll_{coll.id}", use_container_width=True, 
                     type="primary" if st.session_state.current_collection_id == coll.id else "secondary"):
            st.session_state.current_collection_id = coll.id
            st.session_state.current_chat_id = None
            st.rerun()

# -----------------------------------------------------------------------------
# Main Content Area
# -----------------------------------------------------------------------------
if not st.session_state.current_collection_id:
    st.header("Welcome to DocuMind 🧠")
    st.markdown("""
    **DocuMind** is your professional AI-powered document intelligence platform.
    
    👈 **Select or create a Workspace from the sidebar to get started.**
    """)
    st.stop()

# Collection Active View
collection = deps["collection_service"].get_collection(st.session_state.current_collection_id)
if not collection:
    st.session_state.current_collection_id = None
    st.rerun()

st.header(f"📁 {collection.name}")
if collection.description:
    st.caption(collection.description)

tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Documents", "⚡ Productivity Tools"])

# --- TAB 1: Chat ---
with tab1:
    chat_col, hist_col = st.columns([3, 1])
    
    with hist_col:
        st.subheader("Chat History")
        if st.button("➕ New Chat", use_container_width=True):
            session = deps["chat_service"].create_session(collection.id)
            st.session_state.current_chat_id = session.id
            st.rerun()
            
        sessions = deps["chat_service"].get_sessions(collection.id)
        for s in sessions:
            if st.button(f"💬 {s.title}", key=f"chat_{s.id}", use_container_width=True,
                         type="primary" if st.session_state.current_chat_id == s.id else "secondary"):
                st.session_state.current_chat_id = s.id
                st.rerun()
                
    with chat_col:
        if not st.session_state.current_chat_id:
            st.info("Select a chat session or create a new one.")
        else:
            messages = deps["chat_service"].get_messages(st.session_state.current_chat_id)
            for msg in messages:
                with st.chat_message(msg.role):
                    st.markdown(msg.content)
                    if msg.citations:
                        citations = json.loads(msg.citations)
                        for c in citations:
                            st.markdown(f"""<div class="citation-box"><b>📄 {c['source']}</b><br><i>"{c['snippet']}"</i></div>""", unsafe_allow_html=True)
            
            prompt = st.chat_input("Ask about your documents...")
            if prompt:
                # Add user msg to UI instantly
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = deps["chat_service"].send_message(
                            st.session_state.current_chat_id, 
                            collection.id, 
                            prompt
                        )
                        st.markdown(response["answer"])
                        for c in response["citations"]:
                            st.markdown(f"""<div class="citation-box"><b>📄 {c['source']}</b><br><i>"{c['snippet']}"</i></div>""", unsafe_allow_html=True)
                st.rerun()

# --- TAB 2: Documents ---
with tab2:
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader("Upload PDF, DOCX, TXT, or MD", accept_multiple_files=True)
    if st.button("Process Documents"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                for file in uploaded_files:
                    success = deps["document_service"].process_and_add_document(
                        collection.id, file.read(), file.name, file.type
                    )
                    if success:
                        st.success(f"Processed: {file.name}")
                    else:
                        st.error(f"Failed: {file.name}")
            st.rerun()
            
    st.subheader("Document Library")
    if collection.documents:
        for doc in collection.documents:
            st.markdown(f"- **{doc.filename}** ({doc.num_chunks} chunks)")
    else:
        st.info("No documents uploaded yet.")

# --- TAB 3: Productivity Tools ---
with tab3:
    st.subheader("AI Productivity Suite")
    
    prod_col1, prod_col2, prod_col3 = st.columns(3)
    
    with prod_col1:
        if st.button("📝 Executive Summary", use_container_width=True):
            with st.spinner("Generating summary..."):
                summary = deps["productivity_service"].generate_summary(collection.id)
                st.markdown("### Executive Summary")
                st.write(summary)
                
    with prod_col2:
        if st.button("📇 Generate Flashcards", use_container_width=True):
            with st.spinner("Generating flashcards..."):
                flashcards = deps["productivity_service"].generate_flashcards(collection.id)
                st.markdown("### Flashcards")
                st.write(flashcards)
                
    with prod_col3:
        if st.button("❓ Generate Quiz", use_container_width=True):
            with st.spinner("Generating quiz..."):
                quiz = deps["productivity_service"].generate_quiz(collection.id)
                st.markdown("### Quiz")
                st.write(quiz)

    # Delete Collection
    st.divider()
    st.subheader("Settings")
    if st.button("🗑️ Delete Collection", type="primary"):
        deps["collection_service"].delete_collection(collection.id)
        st.session_state.current_collection_id = None
        st.rerun()
