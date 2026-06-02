import pdfplumber
import fitz
from PIL import Image
import io
import os

try:
    from paddleocr import PaddleOCR
    ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')
    PADDLE_AVAILABLE = True
    print("[OCR] PaddleOCR loaded successfully")
except Exception as e:
    PADDLE_AVAILABLE = False
    print(f"[OCR] PaddleOCR not available — will use pdfplumber only. Reason: {e}")


def extract_text_from_pdf(pdf_path: str) -> str:
 
    text = _try_pdfplumber(pdf_path)

    if _is_good_text(text):
        print("[Parser] Digital PDF — used pdfplumber")
        return text.lower()

    if PADDLE_AVAILABLE:
        print("[Parser] Scanned PDF — switching to PaddleOCR")
        text = _try_paddleocr(pdf_path)
        return text.lower()

    print("[Parser] Scanned PDF detected but PaddleOCR unavailable — returning pdfplumber output")
    return text.lower()


def _try_pdfplumber(pdf_path: str) -> str:
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
    except Exception as e:
        print(f"[pdfplumber] Error: {e}")
    return full_text


def _try_paddleocr(pdf_path: str) -> str:
    full_text = ""
    try:
        import numpy as np
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat  = fitz.Matrix(2.0, 2.0)
            pix  = page.get_pixmap(matrix=mat)
            img  = Image.open(io.BytesIO(pix.tobytes("png")))
            img_array = np.array(img)
            result = ocr_engine.ocr(img_array, cls=True)
            if result and result[0]:
                for line in result[0]:
                    full_text += line[1][0] + "\n"
        doc.close()
    except Exception as e:
        print(f"[PaddleOCR] Error: {e}")
    return full_text


def _is_good_text(text: str) -> bool:
    cleaned = text.strip().replace('\n', '').replace(' ', '')
    return len(cleaned) > 100