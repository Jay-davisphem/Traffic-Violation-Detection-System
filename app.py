import threading
import queue
import time
import sqlite3
import cv2
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import Violation, ViolationResponse
from system import TrafficViolationSystem
from config import Config
from image_src import ImageSource
from database import ViolationDatabase

app = FastAPI()

# Mount static files (for CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize the shared image queue and configuration
image_queue = queue.Queue(maxsize=1000)
config = Config()

# Create an instance of your TrafficViolationSystem
system = TrafficViolationSystem(config, image_queue)
processing_thread = None  # Will hold the background thread reference


@app.on_event("startup")
async def startup_event():
    db = ViolationDatabase(config.db_path)
    app.state.image_source = ImageSource(config)
    image_queue = queue.Queue(maxsize=1000)
    app.state.image_source.start_capture(image_queue, db)


# Shutdown event: gracefully stop the background processing system
@app.on_event("shutdown")
async def shutdown_event():
    system.stop()
    if processing_thread is not None:
        processing_thread.join()

def get_recent_violations(limit: int = 10) -> ViolationResponse:
    """
    Fetch the most recent violations from the database and return them as a Pydantic model.
    """
    conn = sqlite3.connect("violations.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, violation_type, confidence, bbox 
        FROM violations 
        ORDER BY timestamp DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    violations = [
        Violation(timestamp=row[0], violation_type=row[1], confidence=row[2], bbox=row[3])
        for row in rows
    ]
    return ViolationResponse(violations=violations)

def generate_frames():
    image_source = app.state.image_source

    while True:
        frame, success = image_source.get_latest_frame()
        if not success or frame is None:
            time.sleep(0.1)
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.1)  # frame rate control

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the main dashboard page with live camera feed and recent violation records.
    """
    violations_response = get_recent_violations()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "violations": violations_response.violations
    })

@app.get("/video_feed")
def video_feed():
    """
    Stream the live camera feed.
    """
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/violations", response_model=ViolationResponse)
def api_violations(limit: int = 10):
    """
    API endpoint to return recent violations as JSON.
    """
    return get_recent_violations(limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
