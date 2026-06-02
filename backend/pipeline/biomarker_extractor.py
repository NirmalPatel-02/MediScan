import re
import json
import os
from config import DATA_DIR

with open(os.path.join(DATA_DIR, 'biomarker_synonyms.json')) as f:
    SYNONYMS = json.load(f)

REVERSE_MAP = {}
for standard_name, aliases in SYNONYMS.items():
    for alias in aliases:
        REVERSE_MAP[alias.lower().strip()] = standard_name

SORTED_ALIASES = sorted(REVERSE_MAP.keys(), key=len, reverse=True)

PLAUSIBLE_RANGES = {
    'haemoglobin':        (3,    25),
    'wbc_count':          (500,  100000),  
    'rbc_count':          (0.5,  10),
    'packed_cell_volume': (5,    75),
    'platelets':          (10,   1500000),
    'mcv':                (50,   150),
    'mch':                (10,   50),
    'mchc':               (20,   45),
    'rdw':                (5,    30),
    'fasting_glucose':    (30,   600),
    'hba1c':              (3,    15),
    'creatinine':         (0.1,  15),
    'blood_urea':         (1,    300),
    'sodium':             (100,  180),
    'potassium':          (1,    10),
    'tot_bilirubin':      (0.1,  30),
    'direct_bilirubin':   (0,    20),
    'alkphos':            (10,   2000),
    'sgpt':               (3,    5000),
    'sgot':               (3,    5000),
    'tot_proteins':       (2,    12),
    'albumin':            (1,    8),
    'ag_ratio':           (0.1,  5),
    'tsh':                (0.001, 100),
    't3':                 (0.3,  5),        
    't4':                 (0.3,  25),
    'total_cholesterol':  (50,   600),
    'ldl':                (10,   500),
    'hdl':                (5,    150),
    'triglycerides':      (10,   3000),
    'vitamin_d':          (1,    250),
    'vitamin_b12':        (50,   5000),
}

MAX_LINE_LENGTH = 250


def extract_biomarkers(raw_text: str) -> dict:

    results = {}
    lines   = [l.strip() for l in raw_text.split('\n')]

    i = 0
    while i < len(lines):
        line = lines[i]

        if not line or len(line) > MAX_LINE_LENGTH:
            i += 1
            continue

        standard_name, matched_alias = _match_biomarker_name(line)
        if not standard_name:
            i += 1
            continue

        value = _extract_value(line, matched_alias)

        if value is None:
            for lookahead in range(1, 4):
                if i + lookahead >= len(lines):
                    break
                next_line = lines[i + lookahead].strip()
                if not next_line or len(next_line) > MAX_LINE_LENGTH:
                    continue
                
                if re.match(r'^\d', next_line):
                    value = _extract_value_from_line(next_line)
                    if value is not None:
                        break

        if value is None:
            i += 1
            continue

        if not _is_plausible(standard_name, value):
            i += 1
            continue

        unit = _extract_unit(line)

        if standard_name not in results:
            results[standard_name] = {
                'value': value,
                'unit':  unit
            }

        i += 1

    return results


def _match_biomarker_name(line: str):
  
    line_lower = line.lower()
    for alias in SORTED_ALIASES:
        pattern = r'(?<![a-z0-9])' + re.escape(alias) + r'(?![a-z0-9])'
        if re.search(pattern, line_lower):
            return REVERSE_MAP[alias], alias
    return None, None


def _extract_value(line: str, biomarker_alias: str) -> float | None:
 
    line_clean  = line.replace(',', '')
    line_lower  = line_clean.lower()
    alias_lower = biomarker_alias.lower()

    alias_pos = line_lower.find(alias_lower)
    if alias_pos == -1:
        return None

    text_after = line_clean[alias_pos + len(alias_lower):]

    text_after = re.sub(r'\b(low|high|borderline|normal|critical|h|l)\b', ' ', text_after, flags=re.IGNORECASE)
    text_after = re.sub(r'\*+', ' ', text_after)

    numbers = re.findall(r'\b(\d+\.?\d*)\b', text_after)
    for num_str in numbers:
        val = float(num_str)
        if 1900 < val < 2100:   
            continue
        if val == 0:
            continue
        return val

    return None


def _extract_value_from_line(line: str) -> float | None:
  
    line_clean = line.replace(',', '')

    line_clean = re.sub(r'\b(low|high|borderline|normal|critical)\b', ' ', line_clean, flags=re.IGNORECASE)
    line_clean = re.sub(r'\*+', ' ', line_clean)

    numbers = re.findall(r'\b(\d+\.?\d*)\b', line_clean)
    for num_str in numbers:
        val = float(num_str)
        if 1900 < val < 2100:
            continue
        if val == 0:
            continue
        return val

    return None


def _is_plausible(biomarker_name: str, value: float) -> bool:
    if biomarker_name not in PLAUSIBLE_RANGES:
        return True  
    low, high = PLAUSIBLE_RANGES[biomarker_name]
    return low <= value <= high


def _extract_unit(line: str) -> str:
    line_lower = line.lower()
    line_lower = line_lower.replace('µ', 'u').replace('μ', 'u')

    units = [
        'thou/ul', 'thou/µl', 'k/mcl', 'm/mcl', 'k/ul', 'm/ul',
        'cells/cumm', 'cells/mcl', 'cells/ul',
        'lakhs/cumm', 'lakhs/ul', 'lakh/cumm',
        'millions/cumm', 'millions/ul', 'mill/cumm', 'million/ul',
        '/cumm', '/mcl', '/ul',
        'mmol/l', 'umol/l', 'nmol/l', 'pmol/l',
        'miu/ml', 'uiu/ml', 'miu/l', 'mu/l', 'iu/l', 'u/l',
        'ng/ml', 'ng/dl', 'ug/ml', 'pg/ml', 'pg/dl',
        'g/dl', 'g/l', 'mg/dl', 'mg/l',
        'gm/dl',
        'meq/l', 'mmhg',
        'seconds', 'sec', 'fl', 'pg', '%',
        'gm%',          
        'g%',           
        'cu micron',    
        '/c.mm',        
        '/c.cmm',
        'mill/cumm',   
        'million/cmm',
    ]

    for unit in units:
        if unit in line_lower:
            return unit

    return 'unknown'