# streamlit_app.py
import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import fitz  # PyMuPDF for PDF parsing
import tempfile
import moviepy.editor as mp  # For basic video processing
import whisper  # For speech-to-text

# Load API key securely from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# UI
st.title("🔬 StudyBuddy")
st.markdown("Generate detailed notes from MCQs, PDFs, and video lectures using web search + Gemini.")

query = st.text_input("Enter your MCQ question or topic:")
additional_instructions = st.text_area("Add custom instructions for note generation:")

uploaded_pdf = st.file_uploader("Upload a PDF (up to 500 pages):", type=["pdf"])
uploaded_video = st.file_uploader("Upload a video lecture (optional):", type=["mp4", "mov", "avi"])

pdf_context = ""
if uploaded_pdf is not None:
    with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
        for page in doc:
            pdf_context += page.get_text()

video_transcript = ""
if uploaded_video is not None:
    st.info("Processing video for audio transcript (this may take a few minutes)...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
        tmp_video.write(uploaded_video.read())
        tmp_video_path = tmp_video.name

    audio_path = tmp_video_path.replace(".mp4", ".wav")
    clip = mp.VideoFileClip(tmp_video_path)
    clip.audio.write_audiofile(audio_path)

    model_whisper = whisper.load_model("base")
    result = model_whisper.transcribe(audio_path)
    video_transcript = result["text"]

if st.button("Generate Notes") and query:
    with st.spinner("Searching web and generating notes..."):
        # Step 1: DuckDuckGo search
        def search_duckduckgo(query, max_results=5):
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r["title"],
                        "snippet": r["body"],
                        "url": r["href"]
                    })
            return results

        search_results = search_duckduckgo(query)
        context_chunks = [res['snippet'] for res in search_results]

        # Step 2: Generate notes
        def generate_notes_with_context(question, context_chunks, pdf_text="", video_text="", custom=""):
            full_context = "\n\n".join(context_chunks)
            prompt = f"""
You are a chemistry expert. Given the following question and context, generate detailed, structured notes:

Question: {question}

User Instructions:
{custom}

Context from search:
{full_context}

Context from uploaded PDF:
{pdf_text}

Context from video lecture transcript:
{video_text}

If the question involves a test, include:
- Discovery
- Reagents and their interactions
- Observations and principles

If it's a mechanism, explain every step clearly.
"""
            response = model.generate_content(prompt)
            return response.text

        notes = generate_notes_with_context(
            query,
            context_chunks,
            pdf_text=pdf_context,
            video_text=video_transcript,
            custom=additional_instructions
        )

        st.subheader("🧪 Generated Notes")
        st.write(notes)

        with st.expander("🔗 Sources"):
            for res in search_results:
                st.markdown(f"- [{res['title']}]({res['url']})")
