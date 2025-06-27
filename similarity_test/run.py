import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

MODEL_OPTIONS = [
    "all-MiniLM-L6-v2",  # Default, should match your request
    "all-mpnet-base-v2",
    "multi-qa-mpnet-base-dot-v1",
    "all-distilroberta-v1",
    "all-MiniLM-L12-v2",
    "multi-qa-distilbert-cos-v1",
]

def compute_semantic_similarities(query, texts, model_name="all-MiniLM-L6-v2"):
    embedder = SentenceTransformer(model_name)
    embeddings = embedder.encode([query] + texts)
    query_emb = embeddings[0]
    sims = [1 - cosine(query_emb, emb) for emb in embeddings[1:]]
    return pd.DataFrame({'Text': texts, 'Semantic Similarity': sims})

st.set_page_config(page_title="Text Similarity (Semantic Only)", layout="wide")
st.title("🧠 Semantic Similarity Calculator")

st.write("Enter a query and multiple texts. Select the model for semantic similarity below:")

with st.form(key="sim_form"):
    query = st.text_area("Enter your query:", placeholder="e.g., Find all mobile payment providers")
    texts_raw = st.text_area("Texts to compare (one per line)",
        placeholder="We offer mobile solutions.\nCompany X specializes in payments...")

    model_name = st.selectbox(
        "Select the SentenceTransformer model:",
        MODEL_OPTIONS,
        index=0
    )

    submit = st.form_submit_button("Calculate Similarities")

if submit:
    texts = [t.strip() for t in texts_raw.strip().split('\n') if t.strip()]
    if not query or not texts:
        st.warning("Please enter a query and at least one text.")
    else:
        with st.spinner("Calculating..."):
            df = compute_semantic_similarities(query, texts, model_name=model_name)
            df = df.sort_values("Semantic Similarity", ascending=False).reset_index(drop=True)

            st.success(f"Calculated for {len(df)} texts.")
            st.dataframe(
                df.style.background_gradient(
                    subset=["Semantic Similarity"], cmap="YlGn"),
                use_container_width=True
            )
else:
    st.caption("Choose a model, enter query and texts, then click Calculate.")

st.markdown("---")
st.markdown(
    "Powered by [Sentence Transformers](https://www.sbert.net/) 🚀"
)
