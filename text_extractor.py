import os
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    return text


def extract_text_from_documents(folder_path):
    all_text = ""
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.endswith(".pdf"):
            all_text += extract_text_from_pdf(file_path)
        elif file_name.endswith(".docx"):
            all_text += extract_text_from_docx(file_path)
        elif file_name.endswith(".txt"):
            all_text += extract_text_from_txt(file_path)
    return all_text


def save_text_to_file(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)



def  content_extractor():
    folder_path = os.getenv("CONTENT_RAW_DIR")
    output_path = os.getenv("CONTENT_DIR_PATH")
    all_text = extract_text_from_documents(folder_path)
    save_text_to_file(all_text, output_path)
