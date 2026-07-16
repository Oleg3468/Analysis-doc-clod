#!/usr/bin/env python3
"""
Agreement Analyzer Mobile API
------------------------------
FastAPI backend for the Quasar/Capacitor mobile app. Exposes endpoints to
analyze an agreement either from raw text or from an uploaded image (OCR).
"""
import io
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analyzer import analyze_text, OCR_AVAILABLE

app = FastAPI(
    title="Agreement Analyzer Mobile API",
    description="Backend API for the Quasar/Capacitor mobile app that scans and analyzes user agreements.",
    version="1.0.0",
)

# Restrict origins via env var in production, e.g. ALLOWED_ORIGINS="https://myapp.com,capacitor://localhost"
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextPayload(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "Agreement Analyzer Mobile API",
        "ocr_available": OCR_AVAILABLE,
    }


@app.post("/analyze-image")
async def analyze_image_endpoint(file: UploadFile = File(...), lang: str = "rus+eng"):
    if not OCR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="OCR is not installed on the server. Run: pip install pillow pytesseract",
        )
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be a valid image")

    from PIL import Image
    import pytesseract

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        extracted_text = pytesseract.image_to_string(image, lang=lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing error: {str(e)}")

    findings = analyze_text(extracted_text)
    return {
        "success": True,
        "text": extracted_text,
        "findings": findings,
    }


@app.post("/analyze-text")
def analyze_text_endpoint(payload: TextPayload):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Field 'text' must not be empty")

    findings = analyze_text(payload.text)
    return {
        "success": True,
        "findings": findings,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
  
