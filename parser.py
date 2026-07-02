"""
parser.py — Hybrid Lab Value Extraction Pipeline
------------------------------------------------
Stage 1: Regex-based extraction (fast, deterministic, zero cost)
Stage 2: LLM-based extraction (fallback when regex yields nothing)

Returns:
{
    "HbA1c": {
        "value": 7.2,
        "unit": "%",
        "ref_low": 4.0,
        "ref_high": 5.6
    }
}
"""

import os
import re
import json
from pypdf import PdfReader
from groq import Groq


# --------------------------------------------------------------------
# Groq Client
# --------------------------------------------------------------------

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --------------------------------------------------------------------
# PDF Utilities
# --------------------------------------------------------------------

def extract_text(file_path: str) -> str:
    """
    Extract text from a PDF.
    Used by app.py.
    """
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def detect_format(file_path: str) -> str:
    """
    Very lightweight detector.

    Returns:
        "digital"
        "scanned"
    """
    text = extract_text(file_path)

    if len(text.strip()) > 30:
        return "digital"

    return "scanned"


# --------------------------------------------------------------------
# Stage 1 : Regex Extraction
# --------------------------------------------------------------------

def extract_lab_values_regex(text: str) -> dict:
    """
    Fast regex extraction.

    Returns:
    {
        test_name:{
            value,
            unit,
            ref_low,
            ref_high
        }
    }
    """

    data = {}

    pattern = re.compile(
        r"(.+?)\s+([-+]?\d*\.?\d+)\s+([^\s]+)\s+(\d*\.?\d+)\s*[-–]\s*(\d*\.?\d+)"
    )

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        match = pattern.search(line)

        if not match:
            continue

        try:

            name, value, unit, low, high = match.groups()

            data[name.strip()] = {
                "value": float(value),
                "unit": unit.strip(),
                "ref_low": float(low),
                "ref_high": float(high),
            }

        except Exception:
            continue

    return data


# --------------------------------------------------------------------
# Stage 2 : LLM Extraction
# --------------------------------------------------------------------

def extract_lab_values_llm(text: str) -> dict:
    """
    LLM fallback extraction.

    Only called when regex finds nothing.
    """

    system_prompt = """
You are a medical report parser.

Extract every laboratory value from the report.

Return ONLY valid JSON.

Example:

{
    "HbA1c":{
        "value":7.2,
        "unit":"%",
        "ref_low":4.0,
        "ref_high":5.6
    }
}

Rules:

- No markdown
- No explanation
- JSON only
- Skip tests without reference ranges
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": text[:5000],
                },
            ],
        )

        raw = response.choices[0].message.content.strip()

        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

        parsed = json.loads(raw)

        cleaned = {}

        for name, values in parsed.items():

            if not isinstance(values, dict):
                continue

            required = ["value", "unit", "ref_low", "ref_high"]

            if not all(k in values for k in required):
                continue

            try:

                cleaned[name] = {
                    "value": float(values["value"]),
                    "unit": str(values["unit"]),
                    "ref_low": float(values["ref_low"]),
                    "ref_high": float(values["ref_high"]),
                }

            except Exception:
                continue

        return cleaned

    except json.JSONDecodeError:
        print("[Parser] Invalid JSON returned by LLM.")
        return {}

    except Exception as e:
        print("[Parser] LLM Extraction Error:", e)
        return {}


# --------------------------------------------------------------------
# Hybrid Parser
# --------------------------------------------------------------------

def extract_lab_values(text: str) -> dict:
    """
    Hybrid Extraction Pipeline

    Stage 1:
        Regex

    Stage 2:
        LLM fallback

    Returns dictionary of lab values.
    """

    regex_results = extract_lab_values_regex(text)

    if regex_results:

        print(
            f"[Parser] Regex extracted {len(regex_results)} values."
        )

        return regex_results

    print(
        "[Parser] Regex found nothing. Switching to LLM..."
    )

    llm_results = extract_lab_values_llm(text)

    if llm_results:

        print(
            f"[Parser] LLM extracted {len(llm_results)} values."
        )

    else:

        print(
            "[Parser] No lab values extracted."
        )

    return llm_results