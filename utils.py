import requests
from bs4 import BeautifulSoup
import PyPDF2
import os
from serpapi import GoogleSearch

### URL Parser ###
def fetch_url_text(source_input):
    urls = [s.strip() for s in source_input.split(",") if s.startswith("http")]
    text_blocks = []
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            text = " ".join([p.text for p in soup.find_all("p")])
            text_blocks.append(text[:1500])
        except:
            text_blocks.append(f"[Error fetching {url}]")
    return "\n\n".join(text_blocks)

### PDF Parser ###
book_to_pdf = {
    "Vogel": "books/vogel.pdf",
    "Clayden": "books/clayden.pdf"
}

def get_book_context(source_input):
    books = [s.strip() for s in source_input.split(",") if not s.startswith("http")]
    texts = []
    for title in books:
        path = book_to_pdf.get(title)
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages[:3]:  # first 3 pages
                    text += page.extract_text()
                texts.append(f"[{title}]\n{text[:1500]}")
        else:
            texts.append(f"[{title}] - PDF not found")
    return "\n\n".join(texts)

### Google Search Summary ###
def google_search_summary(query):
    try:
        params = {
            "q": query,
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "num": 3
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        summaries = []
        for result in results.get("organic_results", [])[:3]:
            summaries.append(result.get("snippet", ""))
        return "\n".join(summaries)
    except:
        return "Google Search failed or no API key set."

### Query Colab LLM ###
def query_colab_llm(prompt):
    try:
        res = requests.post("https://<your-ngrok-endpoint>.ngrok-free.app/predict", json={"prompt": prompt})
        return res.json().get("response", "No response.")
    except:
        return "Error connecting to LLM server."
