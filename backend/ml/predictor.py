import os
import json
import joblib
import pandas as pd
from config import ML_DIR

def _load_pkl(filename):
    path = os.path.join(ML_DIR, filename)
    if not os.path.exists(path):
        print(f"[ML] WARNING: {filename} not found")
        return None
    return joblib.load(path)

def _load_json(filename):
    path = os.path.join(ML_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

liver_model     = _load_pkl('liver_model.pkl')
kidney_model    = _load_pkl('kidney_model.pkl')
liver_features  = _load_json('liver_features.json')
kidney_features = _load_json('kidney_features.json')
liver_medians   = _load_json('liver_medians.json')
kidney_medians  = _load_json('kidney_medians.json')

LIVER_MINIMUM  = ['tot_bilirubin', 'sgpt', 'sgot']
KIDNEY_MINIMUM = ['haemoglobin', 'creatinine']

UNIT_SCALE = {
    'thou/ul':    1000,
    'thou/µl':    1000,
    'thou/μl':    1000,
    'k/mcl':      1000,
    'k/ul':       1000,
    'k/μl':       1000,
    'x10^3/ul':   1000,
    'x10³/ul':    1000,
    'lakhs/cumm': 100000,
    'lakhs/ul':   100000,
    'lakh/cumm':  100000,
    'gm/dl':      1,     
    '/c.mm':   1,  
    'gm%':     1,
}

ALREADY_IN_MILLIONS = {'rbc_count'}

def _scale_value(biomarker_name: str, value: float, unit: str) -> float:
    """Scale value to standard unit before comparison."""
    if biomarker_name in ALREADY_IN_MILLIONS:
        return value

    unit_lower = unit.lower().replace('µ', 'u').replace('μ', 'u')

    for key, multiplier in UNIT_SCALE.items():
        if key in unit_lower:
            return value * multiplier

    return value


REFERENCE_RANGES = {
    # CBC
    'haemoglobin':        {'M': (13.0, 17.0), 'F': (12.0, 15.0)},
    'wbc_count':          {'both': (4000, 11000)},
    'rbc_count':          {'M': (4.5, 5.5),   'F': (3.8, 4.8)},
    'packed_cell_volume': {'M': (40, 52),      'F': (36, 46)},
    'platelets':          {'both': (150000, 410000)},
    'mcv':                {'both': (83, 101)},
    'mch':                {'both': (27.0, 32.0)},
    'mchc':               {'both': (31.5, 34.5)},
    'rdw':                {'both': (11.5, 15.5)},
    # Blood sugar
    'fasting_glucose':    {'both': (70, 99)},
    'hba1c':              {'both': (4.0, 5.6)},
    # Kidney
    'creatinine':         {'M': (0.7, 1.3),   'F': (0.5, 1.1)},
    'blood_urea':         {'both': (7, 20)},
    'sodium':             {'both': (136, 145)},
    'potassium':          {'both': (3.5, 5.0)},
    # Liver
    'tot_bilirubin':      {'both': (0.2, 1.2)},
    'direct_bilirubin':   {'both': (0.0, 0.3)},
    'alkphos':            {'both': (44, 147)},
    'sgpt':               {'both': (7, 56)},
    'sgot':               {'both': (10, 40)},
    'tot_proteins':       {'both': (6.0, 8.3)},
    'albumin':            {'both': (3.4, 5.4)},
    'ag_ratio':           {'both': (1.0, 2.5)},
    'tsh':                {'both': (0.27, 4.2)},
    't3':                 {'both': (0.8, 2.0)},   
    't4':                 {'both': (4.5, 12.5)},   
    'total_cholesterol':  {'both': (0, 200)},
    'ldl':                {'both': (0, 100)},
    'hdl':                {'M': (40, 60),     'F': (50, 80)},
    'triglycerides':      {'both': (0, 150)},
    'vitamin_d':          {'both': (20, 100)},
    'vitamin_b12':        {'both': (200, 900)},
}


def flag_biomarkers(biomarkers: dict, gender: str = 'M') -> dict:

    flagged = {}

    for name, data in biomarkers.items():
        value = data.get('value')
        unit  = data.get('unit', 'unknown')

        if value is None or name not in REFERENCE_RANGES:
            flagged[name] = {**data, 'status': 'UNKNOWN'}
            continue

        scaled    = _scale_value(name, value, unit)
        ref       = REFERENCE_RANGES[name]
        range_key = gender if gender in ref else 'both'

        if range_key not in ref:
            flagged[name] = {**data, 'status': 'UNKNOWN'}
            continue

        low, high = ref[range_key]

        if scaled < low * 0.7 or scaled > high * 1.5:
            status = 'CRITICAL'
        elif scaled < low:
            status = 'LOW'
        elif scaled > high:
            status = 'HIGH'
        else:
            status = 'NORMAL'

        flagged[name] = {
            **data,
            'status':       status,
            'ref_min':      low,
            'ref_max':      high,
            'scaled_value': round(scaled, 3)
        }

    return flagged


def check_diabetes(biomarkers: dict) -> dict:

    hba1c   = biomarkers.get('hba1c', {}).get('value')
    glucose = biomarkers.get('fasting_glucose', {}).get('value')
    result  = {'ran': False}

    if hba1c is not None:
        result['ran']          = True
        result['hba1c']        = hba1c
        result['hba1c_status'] = (
            'DIABETIC_RISK' if hba1c >= 6.5 else
            'PRE_DIABETIC'  if hba1c >= 5.7 else
            'NORMAL'
        )

    if glucose is not None:
        result['ran']             = True
        result['fasting_glucose'] = glucose
        result['glucose_status']  = (
            'DIABETIC_RISK' if glucose >= 126 else
            'PRE_DIABETIC'  if glucose >= 100 else
            'NORMAL'
        )

    if not result['ran']:
        result['reason'] = 'No HbA1c or Fasting Glucose found in report'

    return result


def predict_liver(biomarkers: dict, age: int, gender: str) -> dict:
    if liver_model is None:
        return {'ran': False, 'reason': 'Liver model file not found'}

    missing = [f for f in LIVER_MINIMUM if f not in biomarkers]
    if missing:
        return {
            'ran':    False,
            'reason': f"Missing: {', '.join(missing)}. Upload a Liver Function Test (LFT) report."
        }

    row = {}
    for feat in liver_features:
        if feat == 'age':
            row[feat] = age
        elif feat == 'gender':
            row[feat] = 1 if gender == 'M' else 0
        elif feat in biomarkers:
            row[feat] = biomarkers[feat]['value']
        else:
            row[feat] = liver_medians.get(feat, 0)

    prob = float(liver_model.predict_proba(pd.DataFrame([row])[liver_features])[0][1])

    return {
        'ran':         True,
        'probability': round(prob, 3),
        'risk_level':  'HIGH' if prob > 0.6 else 'MODERATE' if prob > 0.35 else 'LOW',
        'risk_pct':    f"{round(prob * 100)}%"
    }


def predict_kidney(biomarkers: dict, age: int) -> dict:
    if kidney_model is None:
        return {'ran': False, 'reason': 'Kidney model file not found'}

    missing = [f for f in KIDNEY_MINIMUM if f not in biomarkers]
    if missing:
        return {
            'ran':    False,
            'reason': f"Missing: {', '.join(missing)}. Upload a Kidney Function Test (KFT) report."
        }

    row = {}
    for feat in kidney_features:
        if feat == 'age':
            row[feat] = age
        elif feat in biomarkers:
            row[feat] = biomarkers[feat]['value']
        else:
            row[feat] = kidney_medians.get(feat, 0)

    prob = float(kidney_model.predict_proba(pd.DataFrame([row])[kidney_features])[0][1])

    return {
        'ran':         True,
        'probability': round(prob, 3),
        'risk_level':  'HIGH' if prob > 0.6 else 'MODERATE' if prob > 0.35 else 'LOW',
        'risk_pct':    f"{round(prob * 100)}%"
    }


def run_all_predictions(biomarkers: dict, age: int, gender: str) -> dict:
    return {
        'liver':    predict_liver(biomarkers, age, gender),
        'kidney':   predict_kidney(biomarkers, age),
        'diabetes': check_diabetes(biomarkers)
    }