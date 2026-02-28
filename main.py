from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import easyocr
from PIL import Image
import io
import json
import os
import cv2
import numpy as np

app = FastAPI(title="Pro OCR API", description="Advanced Offline/Online OCR Solution")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize readers for common languages to avoid reloading
# We'll use a dictionary to cache readers
readers = {
    'en': easyocr.Reader(['en']),
}

def get_reader(lang='en'):
    if lang not in readers:
        try:
            readers[lang] = easyocr.Reader([lang])
        except Exception as e:
            print(f"Error loading reader for {lang}: {e}")
            return readers['en'] # Fallback to English
    return readers[lang]

@app.get("/")
def home():
    return {"message": "✅ Pro OCR API Running. Use the frontend or /docs."}

@app.post("/ocr/")
async def extract_text(
    file: UploadFile = File(...),
    lang: str = Form("en")
):
    # Allow only image files
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="❌ Only image files (PNG/JPG/JPEG) are allowed."
        )

    # Read file bytes
    image_bytes = await file.read()

    # Convert bytes to numpy array for OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise HTTPException(status_code=400, detail="❌ Invalid image file.")

    # Image Preprocessing
    # 1. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Noise reduction (optional, but usually helpful)
    # gray = cv2.medianBlur(gray, 3)
    
    # 3. Save temp for EasyOCR (it can also take numpy arrays directly)
    # Using numpy array directly is faster
    
    try:
        reader = get_reader(lang)
        result = reader.readtext(gray)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Processing Error: {str(e)}")

    extracted_text = [item[1] for item in result]
    full_text = "\n".join(extracted_text)

    # Prepare output
    output_data = {
        "filename": file.filename,
        "language": lang,
        "raw_text_lines": extracted_text,
        "full_text": full_text
    }

    # Save JSON automatically
    os.makedirs("output", exist_ok=True)
    with open(f"output/{file.filename}_result.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    return {
        "status": "success",
        "data": output_data
    }
