from logger import logger
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
import sqlite3  # Import sqlite3
import time


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/violations", StaticFiles(directory="violations"), name="violations")


# --- Database Connection ---
def get_db_connection():
    try:
        conn = sqlite3.connect("violations.db", check_same_thread=False)  # Replace with your actual db_path
        return conn
    except sqlite3.Error as e:
        logger  .error(f"Database connection error: {e}")
        return None


# --- Latest Frame Retrieval ---
def get_latest_camera_frame_path():
    """Gets the path to the latest image saved in the camera_data directory (assuming sorted by filename)."""
    camera_data_dir = "camera_data"
    if not os.path.exists(camera_data_dir):
        return None
    image_files = [f for f in os.listdir(camera_data_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        return None
    if image_files:
        image_files.sort()
        latest_path = os.path.join(camera_data_dir, image_files[-1])
        logger.info(f"Latest camera frame path: {latest_path}")  # Add this line
        return latest_path
    else:
        return None


# --- FastAPI Routes ---


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM violations")
        violations = cursor.fetchall()
        conn.close()
    else:
        violations = []  # Or handle the error appropriately


    latest_camera_frame_path = get_latest_camera_frame_path()
    return templates.TemplateResponse("index.html", {"request": request, "violations": violations, "latest_camera_frame_path": latest_camera_frame_path})


@app.get("/latest_camera_frame")
async def get_camera_frame():
    latest_camera_frame_path = get_latest_camera_frame_path()
    if latest_camera_frame_path:
        return FileResponse(latest_camera_frame_path, media_type="image/jpeg")
    else:
        return Response(content=b'', media_type="image/jpeg")  # Or a placeholder


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)