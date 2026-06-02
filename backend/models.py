from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age           = Column(Integer, nullable=False)
    gender        = Column(Enum('M', 'F'), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    reports = relationship("Report", back_populates="user")


class Report(Base):
    __tablename__ = "reports"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_date  = Column(String(50))
    lab_name     = Column(String(100))
    health_score = Column(Integer)
    uploaded_at  = Column(DateTime, default=datetime.utcnow)

    user        = relationship("User", back_populates="reports")
    biomarkers  = relationship("BiomarkerResult", back_populates="report")
    predictions = relationship("Prediction", back_populates="report")
    analysis    = relationship("Analysis", back_populates="report", uselist=False)


class BiomarkerResult(Base):
    __tablename__ = "biomarker_results"

    id              = Column(Integer, primary_key=True, index=True)
    report_id       = Column(Integer, ForeignKey("reports.id"), nullable=False)
    biomarker_name  = Column(String(100))
    value           = Column(Float)
    unit            = Column(String(50))
    status          = Column(String(20))   # NORMAL / LOW / HIGH / CRITICAL
    ref_min         = Column(Float)
    ref_max         = Column(Float)
    scaled_value    = Column(Float)

    report = relationship("Report", back_populates="biomarkers")


class Prediction(Base):
    __tablename__ = "predictions"

    id          = Column(Integer, primary_key=True, index=True)
    report_id   = Column(Integer, ForeignKey("reports.id"), nullable=False)
    model_type  = Column(String(20))   # liver / kidney / diabetes
    ran         = Column(Boolean)
    probability = Column(Float)
    risk_level  = Column(String(20))
    risk_pct    = Column(String(10))
    reason      = Column(Text)

    report = relationship("Report", back_populates="predictions")


class Analysis(Base):
    __tablename__ = "analyses"

    id            = Column(Integer, primary_key=True, index=True)
    report_id     = Column(Integer, ForeignKey("reports.id"), nullable=False)
    analysis_text = Column(Text)
    generated_at  = Column(DateTime, default=datetime.utcnow)

    report = relationship("Report", back_populates="analysis")