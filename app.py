from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
# from pyresparser import ResumeParser
# import spacy
from pdf2image import convert_from_path
import pytesseract
import unidecode
from fpdf import FPDF
import os
import tempfile
from flask_cors import CORS
from genai import  structure_resume_data


app = Flask(__name__)
CORS(app, origins=["https://frontend-flask-bpld.vercel.app"])

poppler_path = r"C:\poppler\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(pdf_path):
    app.logger.debug(f"Extracting text from PDF: {pdf_path}")
    reader = PdfReader(pdf_path)
    text_raw = ""

    for i, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text_raw += page_text + "\n"
            app.logger.debug(f"Page {i}: Text extracted successfully.")
        else:
            app.logger.debug(f"Page {i}: No text found.")

    if not text_raw.strip():
        app.logger.info("No text detected in PDF, performing OCR...")
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        ocr_text = ""
        for i, img in enumerate(images, start=1):
            page_text = pytesseract.image_to_string(img)
            ocr_text += page_text + "\n"
            app.logger.debug(f"OCR: Page {i} text extracted.")
        text_raw = ocr_text
        app.logger.info("OCR extraction completed.")

    return text_raw


def save_text_to_pdf(text, output_path):
    app.logger.debug(f"Saving text to PDF: {output_path}")
    pdf_writer = FPDF()
    pdf_writer.set_auto_page_break(auto=True, margin=15)
    pdf_writer.add_page()
    pdf_writer.set_font("Arial", size=12)
    text_clean = unidecode.unidecode(text)
    for line in text_clean.split("\n"):
        pdf_writer.multi_cell(0, 8, line)

    pdf_writer.output(output_path)
    app.logger.debug("PDF saved successfully.")


# def parse_resume(pdf_path):
#     app.logger.info(f"Parsing resume: {pdf_path}")
#     text_raw = extract_text_from_pdf(pdf_path)

#     tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
#     tmp_pdf_path = tmp_pdf.name
#     tmp_pdf.close()
#     save_text_to_pdf(text_raw, tmp_pdf_path)

#     parser_data = ResumeParser(pdf_path).get_extracted_data()
#     print(parser_data)
#     if parser_data.get("name") is None:
#         app.logger.info("Name not found, retrying with OCR PDF...")
#         parser_data = ResumeParser(tmp_pdf_path).get_extracted_data()

#     doc_spacy = nlp(text_raw)
#     filtered_college = [
#         ent.text
#         for ent in doc_spacy.ents
#         if "college" in ent.text.lower() or "university" in ent.text.lower()
#     ]
#     org_entities = [ent.text for ent in doc_spacy.ents if ent.label_ == "ORG"]

#     parser_data["education"] = org_entities
#     parser_data["college_name"] = filtered_college[0] if filtered_college else None

#     if os.path.exists(tmp_pdf_path):
#         os.unlink(tmp_pdf_path)
#         app.logger.debug(f"Temporary OCR PDF deleted: {tmp_pdf_path}")

#     app.logger.info("Resume parsing completed.")
#     return parser_data


@app.route("/parse_resume", methods=["POST"])
def parse_resume_api():
    app.logger.info("Received request to /parse_resume")

    if "resume" not in request.files:
        app.logger.warning("No file part in request.")
        return jsonify({"error": "No file part"}), 400

    file = request.files["resume"]
    if file.filename == "":
        app.logger.warning("No file selected.")
        return jsonify({"error": "No selected file"}), 400

    if file:
        app.logger.info(f"File uploaded: {file.filename}")
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_file_path = tmp_file.name
        tmp_file.close()
        file.save(tmp_file_path)
        app.logger.debug(f"Uploaded file saved to temporary path: {tmp_file_path}")
        resume_data = parse_resume(tmp_file_path)
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
            app.logger.debug(f"Temporary uploaded file deleted: {tmp_file_path}")

        app.logger.info("Returning parsed resume data.")
        return jsonify(resume_data)



@app.route("/genai-parse",methods=["POST"])
def genai_parser():
    if "resume" not in request.files:
        app.logger.warning("No file part in request.")
        return jsonify({"error": "No file part"}), 400

    file = request.files["resume"]
    if file:
        app.logger.info(f"File uploaded: {file.filename}")
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_file_path = tmp_file.name
        tmp_file.close()
        file.save(tmp_file_path)
        app.logger.debug(f"Uploaded file saved to temporary path: {tmp_file_path}")
        resume_data = extract_text_from_pdf(tmp_file_path)
        app.logger.debug("resumedata response",resume_data)
        genai_resp=structure_resume_data(resume_data)
        app.logger.debug("gemini response",genai_resp)
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
            app.logger.debug(f"Temporary uploaded file deleted: {tmp_file_path}")

        app.logger.info("Returning parsed resume data.")
        return jsonify(genai_resp)
    
    
    
@app.route('/')
def home():
    return "Hello, Flask is running on PythonAnywhere!"
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
