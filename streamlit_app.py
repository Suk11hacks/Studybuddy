# streamlit_app.py

import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os

st.set_page_config(page_title="Chemistry Notes Generator", layout="centered")
st.title("🔬 Studybuddy")
st.markdown("""
This app uses **DuckDuckGo** for search and **Gemini (free-tier)** to generate notes from chemistry MCQ questions.
""")

# Gemini setup
gemini_key = st.text_input("🔑 Enter your Gemini API Key:", type="password")
if gemini_key:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("models/gemini-1.5-flash")

# Input question
question = st.text_area("✍️ Enter your chemistry question:",
    placeholder="e.g. Which compound gives a positive Tollen's test?")

# On submit
if st.button("Generate Notes") and question and gemini_key:
    with st.spinner("Searching DuckDuckGo..."):
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(question, max_results=5):
                results.append(f"{r['title']}: {r['body']}")

    # Prompt Gemini
    with st.spinner("Generating detailed notes..."):
        context = "\n\n".join(results)
        prompt = f"""
You are a chemistry expert.
Based on the question and context, generate detailed notes.

Question: {question}
Context: {context}

Include: discovery, reagents, observations, steps of mechanism (if any).
Use clear textbook language.
        """
        response = model.generate_content(prompt)
        st.markdown("### 🧪 Generated Notes:")
        st.write(response.text)

elif not gemini_key:
    st.warning("Please enter your Gemini API key to proceed.")
