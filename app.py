"""
🤖 Autonomous Research Agent - Streamlit Web App
Beautiful UI for AI-powered autonomous research.
"""

import os
import streamlit as st
from agent import ResearchAgent

# ─── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="🤖 Autonomous Research Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    }
    .step-card {
        background: #1e1e2e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .source-chip {
        background: #0f3460;
        color: #fff;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 0.2rem;
        display: inline-block;
    }
    .stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="color:white;font-size:2.5em;">🤖 Autonomous Research Agent</h1>
    <p style="color:#aaa;font-size:1.1em;">
        AI that searches the internet, reads articles, summarizes content,<br>
        and generates reports, blogs, or slides — automatically.
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    output_format = st.selectbox(
        "📄 Output Format",
        options=["report", "blog", "slides"],
        format_func=lambda x: {"report": "📑 Research Paper", "blog": "📝 Blog Post", "slides": "🎯 Presentation Slides"}[x],
    )

    max_sources = st.slider("🌐 Max Sources", min_value=3, max_value=15, value=8)

    st.divider()
    st.header("🔑 API Keys")
    api_key_input = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    use_ollama = st.checkbox("Use Ollama (Local LLM)", value=False)

    if use_ollama:
        ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")
        ollama_model = st.text_input("Ollama Model", value="llama3.2")

    st.divider()
    st.markdown("### 🏗️ Pipeline")
    st.markdown("""
    1. 🔍 Search internet
    2. 📰 Read articles
    3. ✍️ Summarize with LLM
    4. 🗄️ Store in vector DB
    5. 🧠 Synthesize findings
    6. 📄 Generate output
    """)

# ─── Main UI ──────────────────────────────────────────────
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    topic = st.text_input(
        "🔬 Research Topic",
        placeholder="e.g., 'Impact of AI on healthcare in 2025'",
        help="Enter any topic — the agent will research it autonomously",
        label_visibility="collapsed"
    )

with col2:
    research_btn = st.button("🚀 Start Research", type="primary", use_container_width=True)

with col3:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

if clear_btn:
    for key in ["research_result", "agent_instance"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ─── Research Pipeline ────────────────────────────────────
if research_btn and topic.strip():
    # Set API key
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input
    if use_ollama:
        os.environ["USE_OLLAMA"] = "true"
        os.environ["OLLAMA_BASE_URL"] = ollama_url + "/v1"
        os.environ["OLLAMA_MODEL"] = ollama_model

    if not os.getenv("OPENAI_API_KEY") and not use_ollama:
        st.error("⚠️ Please enter an OpenAI API Key or enable Ollama in the sidebar.")
        st.stop()

    # Live progress display
    st.markdown("---")
    st.markdown("### 🔄 Research in Progress...")

    progress_bar = st.progress(0)
    status_container = st.empty()
    steps_container = st.container()

    steps_log = []

    def update_status(step: int, total: int, message: str, icon: str = "⏳"):
        progress = int((step / total) * 100)
        progress_bar.progress(progress)
        status_container.markdown(f"**{icon} {message}**")
        steps_log.append(f"{icon} {message}")
        with steps_container:
            for log in steps_log[-5:]:  # Show last 5 steps
                st.markdown(f"<div class='step-card'>{log}</div>", unsafe_allow_html=True)

    try:
        update_status(1, 6, "Initializing research agent...", "🤖")

        config = {"max_sources": max_sources}
        agent = ResearchAgent(config=config)

        update_status(2, 6, f"Searching the internet for: '{topic}'", "🔍")
        update_status(3, 6, "Reading and extracting article content...", "📰")
        update_status(4, 6, "Summarizing articles with LLM...", "✍️")
        update_status(5, 6, "Synthesizing findings & generating output...", "🧠")

        result = agent.research(topic, output_format=output_format)

        update_status(6, 6, "Research complete!", "✅")
        progress_bar.progress(100)

        st.session_state["research_result"] = result
        st.session_state["agent_instance"] = agent

    except Exception as e:
        st.error(f"❌ Research failed: {str(e)}")
        st.exception(e)

elif research_btn and not topic.strip():
    st.warning("⚠️ Please enter a research topic first.")

# ─── Results Display ──────────────────────────────────────
if "research_result" in st.session_state:
    result = st.session_state["research_result"]
    agent = st.session_state.get("agent_instance")

    st.markdown("---")

    # Metadata banner
    meta = result.get("metadata", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Sources Analyzed", meta.get("source_count", 0))
    with col2:
        st.metric("📄 Output Format", result.get("output_format", "").title())
    with col3:
        st.metric("🕐 Session", meta.get("session_id", "N/A")[:12])

    # Output tabs
    tab1, tab2, tab3 = st.tabs(["📄 Output", "🔗 Sources", "💬 Ask Follow-up"])

    with tab1:
        content = result.get("content", "")
        fmt = result.get("output_format", "report")

        if fmt == "slides":
            st.markdown("### 🎯 Presentation Preview")
            st.components.v1.html(content, height=600, scrolling=True)
            st.download_button(
                "⬇️ Download Slides (HTML)",
                data=content,
                file_name=f"research_{meta.get('session_id', 'output')}_slides.html",
                mime="text/html"
            )
        else:
            st.markdown(content)
            st.download_button(
                f"⬇️ Download {'Report' if fmt == 'report' else 'Blog'} (Markdown)",
                data=content,
                file_name=f"research_{meta.get('session_id', 'output')}_{fmt}.md",
                mime="text/markdown"
            )

    with tab2:
        st.markdown("### 🔗 Sources Used")
        sources = meta.get("sources", [])
        for i, url in enumerate(sources, 1):
            st.markdown(f"**{i}.** [{url}]({url})")

    with tab3:
        st.markdown("### 💬 Ask a Follow-up Question")
        st.info("Ask any question about the research — the agent uses RAG to answer from the sources.")
        question = st.text_input("Your question:", placeholder="What are the main challenges mentioned?")
        if st.button("🔍 Get Answer", type="secondary") and question and agent:
            with st.spinner("Searching research data..."):
                answer = agent.ask(question)
            st.markdown("**Answer:**")
            st.markdown(answer)
