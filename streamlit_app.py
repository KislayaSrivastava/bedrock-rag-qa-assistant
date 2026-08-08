"""
Minimal demo UI for the RAG pipeline. Run with:  streamlit run streamlit_app.py
"""
import streamlit as st

from src.rag_pipeline import RAGPipeline

st.set_page_config(page_title="Bedrock RAG QA Assistant", page_icon="🔎")
st.title("🔎 Bedrock RAG QA Assistant")
st.caption("Ask a question about the ingested documents. Answers are grounded in retrieved context via Amazon Bedrock.")


@st.cache_resource
def load_pipeline() -> RAGPipeline:
    return RAGPipeline()


pipeline = load_pipeline()

if not pipeline.is_ready():
    st.warning("No documents have been ingested yet. Run `python -m src.ingest` first.")
else:
    st.caption(f"Knowledge base ready — {pipeline.chunk_count()} chunks indexed.")

question = st.text_input("Your question")

if st.button("Ask") and question:
    with st.spinner("Retrieving context and generating an answer..."):
        result = pipeline.answer(question)

    st.markdown("### Answer")
    st.write(result["answer"])
    st.caption(f"{result['latency_ms']} ms")

    if result["sources"]:
        st.markdown("### Sources")
        for s in result["sources"]:
            with st.expander(f"{s['source_file']} — score {s['score']}"):
                st.write(s["text_preview"] + "...")
