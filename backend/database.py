from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_USER     = "2hWARrHV14cijb6.root"
DB_PASSWORD = "ffxBc17dYCvv2IrF"
DB_HOST     = "gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com"
DB_PORT     = "4000"
DB_NAME     = "mediscan"


# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl_verify_cert=false&ssl_verify_identity=false"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()