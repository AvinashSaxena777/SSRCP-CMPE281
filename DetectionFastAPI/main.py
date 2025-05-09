from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
import time
from datetime import datetime
from ai_detection import ClientConfig
from ai_detection import VideoStreamer
from ai_detection import DetectionStream
from ai_detection import logger
from fastapi.responses import JSONResponse
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize detection_stream as None at module level
detection_stream = None

@app.on_event("startup")
async def startup_event():
    global detection_stream
    config = ClientConfig.from_env()
    detection_stream = DetectionStream(config)

async def generate_frames(annotated: bool = True):
    global detection_stream
    if not detection_stream or not detection_stream.is_running:
        return
    
    try:
        while detection_stream.is_running:
            frame_data = await detection_stream.get_mjpeg_frame(annotated)
            if frame_data:
                yield frame_data
            await asyncio.sleep(0.03)
    except Exception as e:
        print(f"Error generating frames: {e}")

@app.post("/start")
async def start_detection():
    global detection_stream
    try:
        if not detection_stream:
            return JSONResponse(
                content={"success": False, "message": "Detection stream not initialized"},
                status_code=500
            )
            
        if detection_stream.is_running:
            return {"success": True, "message": "Detection already running"}
        
        result = detection_stream.start()
        if result:
            return {"success": True, "message": "Detection started"}
        else:
            return JSONResponse(
                content={"success": False, "message": "Failed to start detection"},
                status_code=500
            )
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Error: {str(e)}"},
            status_code=500
        )

@app.get("/stream")
async def stream_video():
    return StreamingResponse(generate_frames(annotated=True), 
        media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/original_stream")
async def stream_original_video():
    return StreamingResponse(generate_frames(annotated=False),
        media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/start")
async def start_detection():
    """Start the detection process."""
    global detection_stream
    
    if detection_stream and detection_stream.is_running:
        return {"success": True, "message": "Detection already running"}
    
    if not detection_stream:
        config = ClientConfig.from_env()
        detection_stream = DetectionStream(config)
    
    result = detection_stream.start()
    if result:
        return {"success": True, "message": "Detection started"}
    else:
        return JSONResponse(
            content={"success": False, "message": "Failed to start detection"},
            status_code=500
        )

@app.post("/stop")
async def stop_detection():
    """Stop the detection process."""
    global detection_stream
    
    if detection_stream:
        detection_stream.stop()
    
    return {"success": True, "message": "Detection stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)