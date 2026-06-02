from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def generate_analysis(
    biomarkers:  dict,
    flagged:     dict,
    predictions: dict,
    age:         int,
    gender:      str,
    user_name:   str = "the patient"
) -> str:

    biomarker_lines = []
    for name, data in flagged.items():
        status  = data.get('status', 'UNKNOWN')
        value   = data.get('value', 'N/A')
        unit    = data.get('unit', '')
        ref_min = data.get('ref_min', '')
        ref_max = data.get('ref_max', '')
        if ref_min and ref_max:
            line = f"  - {name}: {value} {unit} [{status}] (normal: {ref_min}–{ref_max})"
        else:
            line = f"  - {name}: {value} {unit} [{status}]"
        biomarker_lines.append(line)

    biomarker_text = "\n".join(biomarker_lines) if biomarker_lines else "No biomarkers extracted."

    prediction_lines = []
    liver = predictions.get('liver', {})
    if liver.get('ran'):
        prediction_lines.append(f"  - Liver Disease Risk: {liver['risk_pct']} ({liver['risk_level']})")
    else:
        prediction_lines.append(f"  - Liver Disease Risk: Not assessed — {liver.get('reason', '')}")

    kidney = predictions.get('kidney', {})
    if kidney.get('ran'):
        prediction_lines.append(f"  - Kidney Disease Risk: {kidney['risk_pct']} ({kidney['risk_level']})")
    else:
        prediction_lines.append(f"  - Kidney Disease Risk: Not assessed — {kidney.get('reason', '')}")

    diabetes = predictions.get('diabetes', {})
    if diabetes.get('ran'):
        parts = []
        if 'hba1c' in diabetes:
            parts.append(f"HbA1c {diabetes['hba1c']}% → {diabetes.get('hba1c_status','')}")
        if 'fasting_glucose' in diabetes:
            parts.append(f"Fasting Glucose {diabetes['fasting_glucose']} mg/dL → {diabetes.get('glucose_status','')}")
        prediction_lines.append(f"  - Diabetes Check: {' | '.join(parts)}")
    else:
        prediction_lines.append(f"  - Diabetes Check: Not assessed — {diabetes.get('reason', '')}")

    prediction_text = "\n".join(prediction_lines)

    prompt = f"""
    You are MediScan, a friendly AI medical report assistant.
    You are speaking directly to {user_name}, a {age}-year-old {'male' if gender == 'M' else 'female'} patient.
    
    BIOMARKER RESULTS:
    {biomarker_text}
    
    ML RISK PREDICTIONS:
    {prediction_text}
    
    YOUR TASK:
    1. Address {user_name} by name in your opening sentence.
    2. Give a friendly overview of the results in plain simple language.
    3. For each biomarker that is LOW, HIGH, or CRITICAL — explain in one sentence what it means.
    4. If any ML risk score ran and is HIGH or MODERATE — explain that condition simply.
    5. Give 2-3 practical lifestyle suggestions specific to these results.
    6. End with: "Please share these results with your doctor for a proper diagnosis. MediScan is for awareness only, not medical advice."
    
    Keep under 300 words. Simple language. No medical jargon.
    """

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis unavailable. Error: {str(e)}"