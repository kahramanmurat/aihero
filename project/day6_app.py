"""
Day 6: Streamlit web interface for the agent
Creates a web UI for interacting with the agent.
"""
import streamlit as st
import asyncio
from day6_ingest import index_data
from day6_search_agent import init_agent
from day6_logs import log_interaction_to_file


# Configuration
REPO_OWNER = "DataTalksClub"
REPO_NAME = "faq"


# --- Initialization ---
@st.cache_resource
def init_agent_cached():
    """Initialize agent with caching to avoid re-indexing on every rerun."""
    def filter(doc):
        return 'data-engineering' in doc['filename']
    
    with st.spinner("🔄 Indexing repository..."):
        index = index_data(REPO_OWNER, REPO_NAME, filter=filter)
    
    agent = init_agent(index, REPO_OWNER, REPO_NAME)
    return agent


# --- Streamlit UI ---
st.set_page_config(
    page_title="AI FAQ Assistant", 
    page_icon="🤖", 
    layout="centered"
)

st.title("🤖 AI FAQ Assistant")
st.caption(f"Ask me anything about the {REPO_OWNER}/{REPO_NAME} repository")

# Initialize agent
agent = init_agent_cached()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# --- Streaming helper ---
def stream_response(prompt: str):
    """Stream agent response."""
    async def agen():
        async with agent.run_stream(user_prompt=prompt) as result:
            last_len = 0
            full_text = ""
            async for chunk in result.stream_output(debounce_by=0.01):
                # Stream only the delta
                new_text = chunk[last_len:]
                last_len = len(chunk)
                full_text = chunk
                if new_text:
                    yield new_text
            # Log once complete
            log_interaction_to_file(agent, result.new_messages())
            st.session_state._last_response = full_text
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    agen_obj = agen()
    
    try:
        while True:
            piece = loop.run_until_complete(agen_obj.__anext__())
            yield piece
    except StopAsyncIteration:
        return


# --- Chat input ---
if prompt := st.chat_input("Ask your question..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Assistant message (streamed)
    with st.chat_message("assistant"):
        response_text = st.write_stream(stream_response(prompt))
    
    # Save full response to history
    final_text = getattr(st.session_state, "_last_response", response_text)
    st.session_state.messages.append({"role": "assistant", "content": final_text})

