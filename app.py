import streamlit as st
import requests

st.title("📘 MCQ RAG Tutor (Gemini)")

question = st.text_area("🧠 Enter MCQ Question")
options = [st.text_input(f"Option {i+1}") for i in range(4)]
urls = st.text_area("🔗 URLs (comma-separated)")
books = st.multiselect("📚 Select books", ["vogel", "clayden"])
use_google = st.checkbox("Include Google Search")

book_data = {
    "vogel": open("books/vogel_sample.txt").read()[:3000],
    "clayden": open("books/clayden_sample.txt").read()[:3000]
}

if st.button("Generate Notes"):
    api_url = st.secrets["RAG_API_URL"]
    payload = {
        "question": question,
        "options": options,
        "urls": [u.strip() for u in urls.split(",") if u.strip()],
        "book_texts": [book_data[b] for b in books],
        "use_google": use_google
    }

    response = requests.post(api_url + "/generate", json=payload)

    if response.status_code == 200:
        st.markdown("### 📄 Generated Notes")
        st.markdown(response.json()["notes"])
    else:
        st.error("Error calling backend.")
