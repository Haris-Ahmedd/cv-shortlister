import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF
import docx2txt
from typing import List
import re

st.set_page_config(page_title="CV Shortlister", layout="centered")
st.title("📄 CV Keyword Shortlister")

st.markdown("Upload CVs (PDF or DOCX), enter required keywords, and this tool will find matching CVs.")

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

# Function to match keywords in text
def match_keywords(text, keywords: List[str]):
    matched = []
    for kw in keywords:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text.lower()):
            matched.append(kw)
    return matched



# File uploader
uploaded_files = st.file_uploader("Upload CVs (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# Keyword input
keyword_input = st.text_input("Enter keywords to match (comma-separated)", placeholder="e.g. Python, Django, API")

if uploaded_files and keyword_input:
    keywords = [kw.strip().lower() for kw in keyword_input.split(",") if kw.strip()]
    st.write(f"🔍 Searching for keywords: {', '.join(keywords)}")

    results = []

    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Extract text
        if suffix == ".pdf":
            text = extract_text_from_pdf(tmp_path)
        elif suffix == ".docx":
            text = extract_text_from_docx(tmp_path)
        else:
            text = ""

        matched = match_keywords(text, keywords)
        score = int((len(matched) / len(keywords)) * 100) if keywords else 0

        results.append({
            "filename": uploaded_file.name,
            "matched_keywords": matched,
            "score": score
        })

    # Show results
    st.subheader("📋 Shortlisted CVs")
    for res in sorted(results, key=lambda x: x["score"], reverse=True):
        st.markdown(f"**{res['filename']}** — ✅ Match: {res['score']}%")
        st.markdown(f"Matched keywords: {', '.join(res['matched_keywords']) if res['matched_keywords'] else 'None'}")
        st.markdown("---")
else:
    st.info("Please upload at least one CV and enter keywords to start.")
