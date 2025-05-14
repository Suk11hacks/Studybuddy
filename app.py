import streamlit as st
from utils import get_book_context, fetch_url_text, google_search_summary, query_colab_llm

st.title("📘 MCQ to Explanatory Notes Generator")

question = st.text_area("📝 Enter the MCQ question:")
options = [st.text_input(f"Option {i+1}", key=f"opt{i}") for i in range(4)]
sources = st.text_area("📚 Suggested sources (URLs or Book Titles, comma-separated):")

if st.button("Generate Notes"):
    url_context = fetch_url_text(sources)
    book_context = get_book_context(sources)
    google_context = google_search_summary(question)

    full_prompt = f"""
MCQ Question: {question}
Options:
A. {options[0]}
B. {options[1]}
C. {options[2]}
D. {options[3]}

Please explain:
1. The concept behind the question.
2. Analyze each option.
3. Describe relevant tests (discovery, mechanism, reagents) if applicable.
4. Explain mechanisms step-by-step if mentioned.
5. Use the provided external context below.

[Context from URLs]
{url_context}

[Context from Book Summaries or PDFs]
{book_context}

[Google Search Summary]
{google_context}
"""
    response = query_colab_llm(full_prompt)
    st.markdown("### 🧠 Generated Notes")
    st.markdown(response)
