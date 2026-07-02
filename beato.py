# import json
# from groq import Groq

# # ── Groq client ──────────────────────────────────────────────────────────────
# # Get your FREE key at https://console.groq.com  (no credit card needed)
# import os
# from groq import Groq

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# # ── Diabetes-relevant tests with normal ranges ────────────────────────────────
# DIABETES_TESTS = {
#     "HbA1c": {
#         "aliases": ["hba1c", "glycated hemoglobin", "glycosylated", "a1c"],
#         "low": 0,
#         "high": 5.6,
#         "critical": 9.0,
#         "unit": "%",
#         "why_it_matters": "3-month blood sugar average"
#     },
#     "Fasting Glucose": {
#         "aliases": ["fasting glucose", "fbs", "fasting blood sugar", "blood glucose"],
#         "low": 70,
#         "high": 100,
#         "critical": 200,
#         "unit": "mg/dL",
#         "why_it_matters": "immediate blood sugar level"
#     },
#     "Creatinine": {
#         "aliases": ["creatinine", "serum creatinine", "s.creatinine"],
#         "low": 0.6,
#         "high": 1.2,
#         "critical": 2.0,
#         "unit": "mg/dL",
#         "why_it_matters": "kidney health indicator"
#     },
#     "Vitamin B12": {
#         "aliases": ["vitamin b12", "b12", "cobalamin", "vit b12"],
#         "low": 200,
#         "high": 900,
#         "critical": 150,
#         "unit": "pg/mL",
#         "why_it_matters": "nerve health — often low in diabetics on Metformin"
#     },
#     "Vitamin D": {
#         "aliases": ["vitamin d", "vit d", "25-oh", "25 hydroxy", "calcidiol"],
#         "low": 30,
#         "high": 100,
#         "critical": 10,
#         "unit": "ng/mL",
#         "why_it_matters": "insulin sensitivity and immunity"
#     },
#     "Hemoglobin": {
#         "aliases": ["hemoglobin", "haemoglobin", "hb", "hgb"],
#         "low": 12.0,
#         "high": 17.0,
#         "critical": 8.0,
#         "unit": "g/dL",
#         "why_it_matters": "anaemia common in diabetic patients"
#     },
#     "TSH": {
#         "aliases": ["tsh", "thyroid stimulating", "thyroid"],
#         "low": 0.4,
#         "high": 4.0,
#         "critical": 10.0,
#         "unit": "mIU/L",
#         "why_it_matters": "thyroid affects blood sugar control"
#     },
#     "Total Cholesterol": {
#         "aliases": ["total cholesterol", "cholesterol", "t.chol"],
#         "low": 0,
#         "high": 200,
#         "critical": 240,
#         "unit": "mg/dL",
#         "why_it_matters": "cardiovascular risk in diabetes"
#     },
# }


# def _match_test(name: str) -> str | None:
#     """
#     Matches a raw lab test name to a known diabetes test.
#     Case-insensitive, checks aliases.
#     """
#     name_lower = name.lower()
#     for standard_name, info in DIABETES_TESTS.items():
#         for alias in info["aliases"]:
#             if alias in name_lower or name_lower in alias:
#                 return standard_name
#     return None


# def flag_diabetes_values(lab_data: dict) -> list:
#     """
#     Takes parsed lab data and returns only diabetes-relevant
#     values with their status flagged.
#     """
#     flagged = []
#     seen = set()  # avoid duplicate matches

#     for raw_name, details in lab_data.items():
#         matched = _match_test(raw_name)

#         if matched and matched not in seen:
#             seen.add(matched)
#             value = details["value"]
#             ranges = DIABETES_TESTS[matched]

#             # Determine status
#             if value < ranges["low"]:
#                 status = "Low"
#             elif value > ranges["high"]:
#                 status = "High"
#             else:
#                 status = "Normal"

#             # Determine if critical
#             is_critical = (
#                 value >= ranges.get("critical", float("inf")) or
#                 value <= ranges.get("critical_low", float("-inf"))
#             )

#             flagged.append({
#                 "test": matched,
#                 "raw_name": raw_name,
#                 "value": value,
#                 "unit": details["unit"],
#                 "ref_low": details["ref_low"],
#                 "ref_high": details["ref_high"],
#                 "status": status,
#                 "is_critical": is_critical,
#                 "why_it_matters": ranges["why_it_matters"],
#             })

#     return flagged


# # def generate_beato_insights(flagged_values: list) -> str:
# #     """
# #     Sends flagged values to Groq LLM and gets
# #     BeatO-style diabetes coaching insights.
# #     """
# #     if not flagged_values:
# #         return "No diabetes-relevant values found in this report."

# #     # Only send the fields the LLM needs
# #     clean_values = [
# #         {
# #             "test": v["test"],
# #             "value": v["value"],
# #             "unit": v["unit"],
# #             "status": v["status"],
# #             "is_critical": v["is_critical"],
# #             "why_it_matters": v["why_it_matters"],
# #         }
# #         for v in flagged_values
# #     ]

# #     prompt = f"""
# # You are an AI health coach for BeatO, India's leading diabetes management app.
# # A patient's lab report has been analysed and the following values were found:

# # {json.dumps(clean_values, indent=2)}

# # Write 3 short, warm, and specific coaching insights that BeatO's care team 
# # should act on. Structure your response exactly like this:

# # 1. 🩸 Blood Sugar Control: [insight about HbA1c or glucose if present]
# # 2. ⚠️ Complication Risk: [insight about kidneys/nerves/anaemia if relevant values present]  
# # 3. 📅 Recommended Action: [specific next step — glucometer check schedule, doctor visit, or supplement]

# # Rules:
# # - Use simple Hindi-friendly English (avoid jargon)
# # - Be warm and encouraging, not scary
# # - Be specific to the actual values, not generic
# # - If a value is critical, flag it clearly but calmly
# # - Keep each point to 2 sentences max
# # """

# #     response = client.chat.completions.create(
# #         model="llama3-70b-8192",
# #         messages=[{"role": "user", "content": prompt}],
# #         max_tokens=400,
# #         temperature=0.4,
# #     )

# #     return response.choices[0].message.content


# def explain_consequences(flagged_values: list, language: str = "English") -> str:
    
#     prompt = f"""
# The user is not tech savvy and doesn't understand 
# medical jargon so you have to tell them about 
# their test results in a way that is easy to 
# understand. Suggest possible precautions they 
# can take. Don't scare them with possible effects, 
# just make them aware.
# Also specifically mention — even a small injury 
# or cut should not be ignored by a diabetic patient 
# and must be shown to a doctor immediately.
# Respond in {language} only.
# Values: {flagged_values}
# """
    
#     response = client.chat.completions.create(
#         model="llama3-70b-8192",
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=400,
#         temperature=0.4,
#     )

#     return response.choices[0].message.content

# def get_risk_score(flagged_values: list) -> tuple[int, str]:
#     """
#     Calculates a simple 0-100 diabetes risk score
#     based on number and severity of abnormal values.
#     Returns (score, category).
#     """
#     if not flagged_values:
#         return 0, "No Data"

#     score = 0
#     for v in flagged_values:
#         if v["is_critical"]:
#             score += 30
#         elif v["status"] != "Normal":
#             score += 15

#     score = min(score, 100)

#     if score == 0:
#         category = "✅ All Clear"
#     elif score <= 30:
#         category = "🟡 Monitor Closely"
#     elif score <= 60:
#         category = "🟠 Needs Attention"
#     else:
#         category = "🔴 Urgent Review"

#     return score, category










import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DIABETES_TESTS = {
    "HbA1c":{"aliases":["hba1c","glycated hemoglobin","glycosylated","a1c"],"low":0,"high":5.6,"critical":9.0,"unit":"%","why_it_matters":"3-month blood sugar average"},
    "Fasting Glucose":{"aliases":["fasting glucose","fbs","fasting blood sugar","blood glucose"],"low":70,"high":100,"critical":200,"unit":"mg/dL","why_it_matters":"immediate blood sugar level"},
    "Creatinine":{"aliases":["creatinine","serum creatinine","s.creatinine"],"low":0.6,"high":1.2,"critical":2.0,"unit":"mg/dL","why_it_matters":"kidney health indicator"},
    "Vitamin B12":{"aliases":["vitamin b12","b12","cobalamin","vit b12"],"low":200,"high":900,"critical":150,"unit":"pg/mL","why_it_matters":"nerve health"},
    "Vitamin D":{"aliases":["vitamin d","vit d","25-oh","25 hydroxy","calcidiol"],"low":30,"high":100,"critical":10,"unit":"ng/mL","why_it_matters":"insulin sensitivity and immunity"},
    "Hemoglobin":{"aliases":["hemoglobin","haemoglobin","hb","hgb"],"low":12,"high":17,"critical":8,"unit":"g/dL","why_it_matters":"anaemia common in diabetic patients"},
    "TSH":{"aliases":["tsh","thyroid stimulating","thyroid"],"low":0.4,"high":4.0,"critical":10,"unit":"mIU/L","why_it_matters":"thyroid affects blood sugar control"},
    "Total Cholesterol":{"aliases":["total cholesterol","cholesterol","t.chol"],"low":0,"high":200,"critical":240,"unit":"mg/dL","why_it_matters":"cardiovascular risk in diabetes"},
}

def _match_test(name:str):
    n=name.lower()
    for std,info in DIABETES_TESTS.items():
        for a in info["aliases"]:
            if a in n or n in a:
                return std
    return None

def flag_diabetes_values(lab_data:dict)->list:
    out=[]; seen=set()
    for raw,d in lab_data.items():
        m=_match_test(raw)
        if not m or m in seen: continue
        seen.add(m); r=DIABETES_TESTS[m]; v=d["value"]
        status="Normal"
        if v<r["low"]: status="Low"
        elif v>r["high"]: status="High"
        out.append({
            "test":m,"raw_name":raw,"value":v,"unit":d["unit"],
            "ref_low":d["ref_low"],"ref_high":d["ref_high"],
            "status":status,
            "is_critical":v>=r["critical"],
            "why_it_matters":r["why_it_matters"]
        })
    return out

def generate_beato_insights(flagged_values:list)->str:
    return explain_consequences(flagged_values,"English")

def explain_consequences(flagged_values:list, language:str="English")->str:
    if not flagged_values:
        return "No diabetes-relevant values found in this report."
    prompt=f"""
You are BeatO's AI diabetes coach.
Respond ONLY in {language}.
Explain the patient's lab values in simple language.
Suggest practical precautions.
Do not use medical jargon.
Do not frighten the patient.
Mention that even a small cut or wound should not be ignored by diabetic patients and should be shown to a doctor.
Lab values:
{json.dumps(flagged_values,indent=2)}
"""
    resp=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":prompt}],
        temperature=0.4,
        max_tokens=500,
    )
    return resp.choices[0].message.content

def get_risk_score(flagged_values:list):
    if not flagged_values: return 0,"No Data"
    score=0
    for v in flagged_values:
        if v["is_critical"]: score+=30
        elif v["status"]!="Normal": score+=15
    score=min(score,100)
    if score==0: cat="✅ All Clear"
    elif score<=30: cat="🟡 Monitor Closely"
    elif score<=60: cat="🟠 Needs Attention"
    else: cat="🔴 Urgent Review"
    return score,cat











