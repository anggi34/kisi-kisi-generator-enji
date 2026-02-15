import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
import re

st.set_page_config(page_title="Kisi-Kisi Generator Pro", layout="wide")

st.title("📚 Kisi-Kisi Indikator Generator (Upload Word)")

uploaded_file = st.file_uploader("Upload File Soal (.docx)", type=["docx"])

def detect_questions(text):
    pattern = r'^\s*\d+[\.\)]?\s+'
    questions = []
    lines = text.split("\n")
    current_question = ""

    for line in lines:
        if re.match(pattern, line):
            if current_question:
                questions.append(current_question.strip())
            current_question = line
        else:
            current_question += " " + line

    if current_question:
        questions.append(current_question.strip())

    return questions

def auto_level(text):
    text = text.lower()
    if "sebutkan" in text:
        return "C1"
    elif "jelaskan" in text:
        return "C2"
    elif "terapkan" in text or "gunakan" in text:
        return "C3"
    elif "analisis" in text:
        return "C4"
    else:
        return "C2"

if uploaded_file:

    doc = Document(uploaded_file)
    full_text = "\n".join([para.text for para in doc.paragraphs])

    questions = detect_questions(full_text)

    st.success(f"{len(questions)} soal terdeteksi.")

    mode = st.radio("Pilih Mode Level:", ["Manual", "Otomatis"])

    levels = []
    indicators = []

    if mode == "Manual":
        for i, q in enumerate(questions):
            level = st.selectbox(
                f"Soal {i+1} Level",
                ["C1", "C2", "C3", "C4", "C5", "C6"],
                key=i
            )
            levels.append(level)
            indicators.append(f"Siswa mampu menyesuaikan indikator level {level} pada soal nomor {i+1}.")
    else:
        for i, q in enumerate(questions):
            level = auto_level(q)
            levels.append(level)
            indicators.append(f"Siswa mampu menyesuaikan indikator level {level} pada soal nomor {i+1}.")

    if st.button("Generate & Download Excel"):
        df = pd.DataFrame({
            "No": range(1, len(indicators)+1),
            "Level": levels,
            "Indikator": indicators
        })

        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        st.download_button(
            label="Download Excel",
            data=output,
            file_name="kisi_kisi_indikator.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

