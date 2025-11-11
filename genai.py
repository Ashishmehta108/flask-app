import os
import json
import re
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = Client(api_key=API_KEY)


def structure_resume_data(prompt: str):
    """
    Sends resume text to Gemini and returns a fully validated, sanitized, and
    well-structured JSON object suitable for frontend consumption.
    """

    instruction = f"""
You are a professional resume parser and summarizer.
Analyze the resume content below and output structured JSON strictly following this schema.

DO NOT include explanations, markdown, or code fences — only return valid JSON.

Expected JSON structure:
{{
  "name": "",
  "description": "",  // AI-inferred 2–3 line professional summary
  "contact_info": {{
    "email": "",
    "phone": "",
    "address": "",
    "linkedin": "",
    "github": "",
    "portfolio": ""
  }},
  "summary": "",
  "skills": [
    {{
      "category": "",
      "items": []
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "location": "",
      "start_date": "",
      "end_date": "",
      "grade": ""
    }}
  ],
  "experiences": [
    {{
      "title": "",
      "company": "",
      "location": "",
      "start_date": "",
      "end_date": "",
      "description": ""
    }}
  ],
  "projects": [
    {{
      "name": "",
      "description": "",
      "technologies": [],
      "link": ""
    }}
  ],
  "certifications": [
    {{
      "name": "",
      "issuer": "",
      "date": ""
    }}
  ],
  "achievements": [
    {{
      "title": "",
      "description": ""
    }}
  ],
  "other_information": [
    {{
      "type": "",
      "details": ""
    }}
  ]
}}

Additional Rules:
- “description” must be an AI-inferred short professional bio (2–3 sentences).
- Keep fields concise and accurate; do not add irrelevant info.
- Ensure output is valid JSON without markdown or comments.

Now parse and infer from the following resume content:
{prompt}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=instruction
    )

    # --- Clean up model output ---
    text = response.text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError:
        parsed_json = {"error": "Failed to parse JSON", "raw_text": text}

    # --- Sanitize and validate output ---
    validated = validate_resume_json(parsed_json)
    return validated


def validate_resume_json(data):
    """Ensure all keys exist, fill missing with defaults, and normalize empty values."""

    def safe_str(val):
        if not val or not isinstance(val, str) or val.strip() == "":
            return None
        return val.strip()

    def safe_list(val):
        if not val or not isinstance(val, list):
            return []
        return [v for v in val if v]

    # Default schema to guarantee consistency
    default_schema = {
        "name": None,
        "description": None,
        "contact_info": {
            "email": None,
            "phone": None,
            "address": None,
            "linkedin": None,
            "github": None,
            "portfolio": None,
        },
        "summary": None,
        "skills": [],
        "education": [],
        "experiences": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
        "other_information": [],
    }

    # Merge with defaults (deep merge)
    def deep_merge(default, incoming):
        if isinstance(default, dict):
            merged = {}
            for key, val in default.items():
                if key in incoming and incoming[key] is not None:
                    merged[key] = deep_merge(val, incoming[key])
                else:
                    merged[key] = val
            return merged
        elif isinstance(default, list):
            return safe_list(incoming)
        else:
            return safe_str(incoming)

    sanitized = deep_merge(default_schema, data if isinstance(data, dict) else {})

    return sanitized


# Example usage
if __name__ == "__main__":
    test_resume = """
    Jane Doe
    Email: jane.doe@gmail.com | Phone: +1 555 123 4567
    LinkedIn: linkedin.com/in/janedoe | GitHub: github.com/janedoe
    Address: Bangalore, India

    Summary:
    Experienced frontend engineer with expertise in React, Next.js, and UI/UX development.

    Skills:
    - Frontend: React, Next.js, TailwindCSS
    - Backend: Node.js, Express
    - Tools: Git, Figma

    Education:
    B.Tech in Computer Science, NIT Trichy (2016–2020), GPA: 8.7/10

    Experience:
    Frontend Engineer at Flipkart (2020–Present)
    Worked on performance optimization, dark mode architecture, and component libraries.

    Projects:
    - E-commerce Dashboard: Built a scalable admin panel using React and ShadCN UI.
    """

    result = structure_resume_data(test_resume)
    print(json.dumps(result, indent=2))
