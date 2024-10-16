from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from typing import List
import uuid
from pydantic import BaseSettings


class Settings(BaseSettings):
    BASE_URL: str = "http://localhost:8000"


settings = Settings()

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Create a directory to store uploaded images
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Function to get list of uploaded images
def get_uploaded_images() -> List[dict]:
    return [
        {"filename": f, "url": f"{settings.BASE_URL}/static/uploads/{f}"}
        for f in os.listdir(UPLOAD_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    images = get_uploaded_images()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "images": images, "base_url": settings.BASE_URL},
    )


@app.post("/upload")
async def upload_images(files: List[UploadFile] = File(...)):
    uploaded_files = []
    for file in files:
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_files.append(
            {
                "filename": new_filename,
                "url": f"{settings.BASE_URL}/static/uploads/{new_filename}",
            }
        )
    return {"uploaded_files": uploaded_files}


@app.get("/images")
async def list_images():
    images = get_uploaded_images()
    return {"images": images}
