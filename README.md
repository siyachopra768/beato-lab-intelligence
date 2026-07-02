# 🩺 BeatO Lab Intelligence

## The Problem

Someone close to me is a diabetic patient. A small wound 
from an injury led to plastic surgery because the skin 
deteriorated — something that could have been prevented 
with early awareness.

This made me realise that people are often unaware of 
how serious diabetes really is. They get lab reports 
with numbers they don't understand and put them in a 
drawer. Nobody tells them what those numbers mean for 
their daily life.

## What This Does

- Reads any Indian lab report PDF (SRL, Metropolis, Thyrocare)
- Extracts diabetes-relevant values — HbA1c, creatinine, 
  Vitamin B12, hemoglobin and more
- Explains what those values mean in simple language
- Warns patients that even a small cut must not be ignored
- Available in Hindi and English

## Why It's Different

BeatO's SugarGPT only sees glucometer readings — 
this app adds full lab report visibility with 
plain-language consequence explanations for patients 
who don't understand medical jargon.

## Tech Stack

- Python
- Streamlit
- Groq (LLaMA 3) — free API
- PyPDF

## How To Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set your Groq API key:
```bash
export GROQ_API_KEY="your_key_here"
```
Get a free key at https://console.groq.com

## Demo

https://beato-lab-intelligence-7e8oqez84hepcnpzxb8mnr.streamlit.app/

---

*Built as a feature demonstration for BeatO's diabetes 
coaching workflow. Not for medical use.*
