# import spacy
# from spacy.pipeline import EntityRuler
# from PyPDF2 import PdfReader
# import re

# nlp = spacy.load("en_core_web_sm")

# ruler = nlp.add_pipe("entity_ruler", before="ner")

# patterns = [
#     {"label": "EMAIL", "pattern": [{"TEXT": {"REGEX": r"[^@\s]+@[^@\s]+\.[^@\s]+"}}]},
#     {
#         "label": "PHONE",
#         "pattern": [
#             {
#                 "TEXT": {
#                     "REGEX": r"(\+?\d{1,3}[-.\s]?)?(\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}|\d{10})"
#                 }
#             }
#         ],
#     },
#     {
#         "label": "EDUCATION",
#         "pattern": [
#             {
#                 "LOWER": {
#                     "IN": [
#                         "bachelor",
#                         "b.tech",
#                         "b.sc",
#                         "b.e",
#                         "master",
#                         "m.tech",
#                         "msc",
#                         "mba",
#                         "bca",
#                         "bachelor of technology",
#                         "bachelor of science",
#                         "bachelor of engineering",
#                         "master of technology",
#                         "master of science",
#                     ]
#                 }
#             }
#         ],
#     },
#     {
#         "label": "EXPERIENCE",
#         "pattern": [
#             {"LOWER": {"IN": ["experience", "internship", "projects", "worked"]}}
#         ],
#     },
#     {
#         "label": "LOCATION",
#         "pattern": [{"LOWER": {"IN": ["city", "state", "country", "address"]}}],
#     },
# ]

# ruler.add_patterns(patterns)

# pdf_path = "./pdf/resume.pdf"
# text = ""
# for page in PdfReader(pdf_path).pages:
#     page_text = page.extract_text()
#     if page_text:
#         text += page_text + "\n"


# doc = nlp(text)

# filtered_ents = [
#     ent
#     for ent in doc.ents
#     if ("college" in ent.text.lower() or "university" in ent.text.lower())
# ]
# print(filtered_ents)

# doc.ents = filtered_ents

# data = {
#     "Phone": [ent.text for ent in doc.ents if ent.label_ == "PHONE"],
#     "Education": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
#     "Experience": [ent.text for ent in doc.ents if ent.label_ == "EXPERIENCE"],
#     "Location": [ent.text for ent in doc.ents if ent.label_ == "LOCATION"],
# }

# print("\n--- Extracted Data ---")
# for key, value in data.items():
#     print(f"{key}: {value}")
