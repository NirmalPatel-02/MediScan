from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import shutil, os, tempfile
from datetime import datetime

from pipeline.ocr_parser          import extract_text_from_pdf
from pipeline.biomarker_extractor import extract_biomarkers
from ml.predictor                 import flag_biomarkers, run_all_predictions
from rag.groq_explainer           import generate_analysis

router = APIRouter(prefix="/reports", tags=["Reports"])


def compute_health_score(flagged: dict) -> int:
  
    if not flagged:
        return 50

    total   = len(flagged)
    points  = 0

    for data in flagged.values():
        status = data.get('status', 'UNKNOWN')
        if status == 'NORMAL':
            points += 10
        elif status in ('LOW', 'HIGH'):
            points += 5
        elif status == 'CRITICAL':
            points += 0
        else:
            points += 7

    raw_score = (points / (total * 10)) * 100
    return max(0, min(100, round(raw_score)))


@router.post("/analyse")
async def analyse_report(
    file:         UploadFile = File(...),
    db:           Session    = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    suffix = os.path.splitext(file.filename)[1] or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        raw_text = extract_text_from_pdf(tmp_path)
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

        biomarkers = extract_biomarkers(raw_text)
        if not biomarkers:
            raise HTTPException(status_code=400, detail="No biomarkers found in this report.")

        flagged = flag_biomarkers(biomarkers, gender=current_user.gender)

        predictions = run_all_predictions(
            biomarkers = biomarkers,
            age        = current_user.age,
            gender     = current_user.gender
        )

        health_score = compute_health_score(flagged)

        analysis = generate_analysis(
            biomarkers  = biomarkers,
            flagged     = flagged,
            predictions = predictions,
            age         = current_user.age,
            gender      = current_user.gender,
            user_name   = current_user.name    
        )

        report = models.Report(
            user_id      = current_user.id,
            report_date  = str(datetime.utcnow().date()),
            lab_name     = "Unknown",
            health_score = health_score,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

 
        for name, data in flagged.items():
            bm = models.BiomarkerResult(
                report_id      = report.id,
                biomarker_name = name,
                value          = data.get('value'),
                unit           = data.get('unit'),
                status         = data.get('status'),
                ref_min        = data.get('ref_min'),
                ref_max        = data.get('ref_max'),
                scaled_value   = data.get('scaled_value')
            )
            db.add(bm)

        for model_type, pred in predictions.items():
            p = models.Prediction(
                report_id   = report.id,
                model_type  = model_type,
                ran         = pred.get('ran', False),
                probability = pred.get('probability'),
                risk_level  = pred.get('risk_level'),
                risk_pct    = pred.get('risk_pct'),
                reason      = pred.get('reason')
            )
            db.add(p)

        db.add(models.Analysis(
            report_id     = report.id,
            analysis_text = analysis
        ))

        db.commit()

        return {
            "status":           "success",
            "report_id":        report.id,
            "user":             current_user.name,
            "health_score":     health_score,
            "biomarkers_found": len(biomarkers),
            "biomarkers":       flagged,
            "predictions":      predictions,
            "analysis":         analysis
        }

    finally:
        os.remove(tmp_path)


@router.get("/history")
def get_history(
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    reports = (
        db.query(models.Report)
        .filter(models.Report.user_id == current_user.id)
        .order_by(models.Report.uploaded_at.desc())
        .all()
    )

    return {
        "user":    current_user.name,
        "total":   len(reports),
        "reports": [
            {
                "report_id":    r.id,
                "uploaded_at":  str(r.uploaded_at),
                "health_score": r.health_score,
                "biomarkers_found": len(r.biomarkers)
            }
            for r in reports
        ]
    }


@router.get("/{report_id}")
def get_report(
    report_id:    int,
    db:           Session     = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    report = db.query(models.Report).filter(
        models.Report.id      == report_id,
        models.Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "report_id":    report.id,
        "uploaded_at":  str(report.uploaded_at),
        "health_score": report.health_score,
        "biomarkers": [
            {
                "name":         b.biomarker_name,
                "value":        b.value,
                "unit":         b.unit,
                "status":       b.status,
                "ref_min":      b.ref_min,
                "ref_max":      b.ref_max,
                "scaled_value": b.scaled_value
            }
            for b in report.biomarkers
        ],
        "predictions": [
            {
                "model":       p.model_type,
                "ran":         p.ran,
                "probability": p.probability,
                "risk_level":  p.risk_level,
                "risk_pct":    p.risk_pct,
                "reason":      p.reason
            }
            for p in report.predictions
        ],
        "analysis": report.analysis.analysis_text if report.analysis else None
    }