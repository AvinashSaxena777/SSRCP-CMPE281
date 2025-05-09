import os
import sys
import time
import logging
import asyncio
from typing import Iterator, Optional
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor

import cv2
import grpc
import numpy as np

# Import proto definitions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from protos import detection_pb2, detection_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fastapi-streaming-client")

@dataclass
class ClientConfig:
    """Configuration parameters for the client."""
    server_address: str = "localhost:50051"
    camera_source: str = 0  # 0 for default webcam
    frame_skip: int = 2  # Process every n-th frame
    display_width: int = 1280
    display_height: int = 720
    max_retries: int = 3
    retry_delay: float = 2.0  # seconds
    table_width: int = 500
    font_scale: float = 0.5

    @classmethod
    def from_env(cls) -> 'ClientConfig':
        """Load configuration from environment variables."""
        return cls(
            server_address=os.getenv("TRACKING_SERVER_ADDRESS", "localhost:50051"),
            camera_source=os.getenv("TRACKING_CAMERA_SOURCE", "demo-fire.mp4"),
            frame_skip=int(os.getenv("TRACKING_FRAME_SKIP", "2")),
            display_width=int(os.getenv("TRACKING_DISPLAY_WIDTH", "1280")),
            display_height=int(os.getenv("TRACKING_DISPLAY_HEIGHT", "720")),
            max_retries=int(os.getenv("TRACKING_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("TRACKING_RETRY_DELAY", "2.0")),
            table_width=int(os.getenv("TRACKING_TABLE_WIDTH", "500")),
            font_scale=float(os.getenv("TRACKING_FONT_SCALE", "0.5")),
        )

class VideoStreamer:
    """Handles video file input and frame serving"""
    def __init__(self, config: ClientConfig):
        self.config = config
        self.frame_processor = FrameProcessor()
        self.cap = None
        self.channel = None
        self.stub = None
        self.is_running = False
        self.detection_active = False
        self.original_frame = None
        self.annotated_frame = None
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=2)

    def start(self) -> bool:
        try:
            # Connect to gRPC server
            self.channel = grpc.insecure_channel(
                self.config.server_address,
                options=[('grpc.max_message_length', 50 * 1024 * 1024)]
            )
            self.stub = detection_pb2_grpc.DetectionServiceStub(self.channel)
            
            # Open video file
            self.cap = cv2.VideoCapture(self.config.video_source)
            if not self.cap.isOpened():
                logger.error(f"Cannot open video file: {self.config.video_source}")
                return False

            self.is_running = True
            self.executor.submit(self._process_frames)
            return True
        except Exception as e:
            logger.error(f"Failed to start video stream: {e}")
            self.stop()
            return False

    def _request_generator(self) -> Iterator[detection_pb2.FrameRequest]:
        count = 0
        robot_id = os.getenv("ROBOT_ID", "robot_1")

        while self.is_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                # Loop video when finished
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if count % self.config.frame_skip != 0:
                count += 1
                continue

            # Resize and store original frame
            frame = self.frame_processor.resize_frame(frame, 
                self.config.display_width, self.config.display_height)
            
            with self.lock:
                self.original_frame = frame.copy()

            encoded = self.frame_processor.encode_frame(frame)
            if encoded:
                yield detection_pb2.FrameRequest(
                    robot_id=robot_id,
                    timestamp=int(time.time() * 1000),
                    frame=encoded
                )
            count += 1


class FrameProcessor:
    """Handles frame encoding and decoding operations."""

    @staticmethod
    def encode_frame(frame: np.ndarray, quality: int = 90) -> Optional[bytes]:
        """Encode a frame as JPEG bytes."""
        try:
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
            success, buffer = cv2.imencode('.jpg', frame, encode_params)
            return buffer.tobytes() if success else None
        except Exception as e:
            logger.error(f"Failed to encode frame: {e}")
            return None

    @staticmethod
    def decode_frame(frame_bytes: bytes) -> Optional[np.ndarray]:
        """Decode a frame from bytes."""
        try:
            frame_np = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            logger.error(f"Failed to decode frame: {e}")
            return None

    @staticmethod
    def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
        """Resize a frame to the specified dimensions."""
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

class DetectionStream:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.frame_processor = FrameProcessor()
        self.cap = None
        self.channel = None
        self.stub = None
        self.is_running = False
        self.detection_active = False
        self.original_frame = None
        self.annotated_frame = None
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def start(self) -> bool:
        """Start the detection stream."""
        try:
            # Connect to gRPC server
            self.channel = grpc.insecure_channel(
                self.config.server_address,
                options=[
                    ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
                    ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 MB
                    ('grpc.keepalive_time_ms', 30000),  # Send keepalive ping every 30s
                    ('grpc.keepalive_timeout_ms', 10000),  # Keepalive ping timeout after 10s
                ]
            )
            self.stub = detection_pb2_grpc.DetectionServiceStub(self.channel)
            logger.info(f"Connected to detection server at {self.config.server_address}")
            
            # Open camera
            self.cap = cv2.VideoCapture(self.config.camera_source)
            if not self.cap.isOpened():
                logger.error(f"Cannot open camera source: {self.config.camera_source}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.display_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.display_height)
            
            # Start the processing loop in a separate thread
            self.is_running = True
            self.executor.submit(self._process_frames)
            
            return True
        except Exception as e:
            logger.error(f"Failed to start detection stream: {e}")
            self.stop()
            return False
    
    def stop(self) -> None:
        """Stop the detection stream."""
        self.is_running = False
        
        # Release resources
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None
        
        logger.info("Detection stream stopped")
    
    def _request_generator(self) -> Iterator[detection_pb2.FrameRequest]:
        """Generate streaming requests for the gRPC service."""
        count = 0
        robot_id = os.getenv("ROBOT_ID", "robot_1")
        
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to read frame from camera")
                break
            
            # Frame throttling
            if count % self.config.frame_skip != 0:
                count += 1
                continue
            
            # Resize if needed
            if frame.shape[1] != self.config.display_width or frame.shape[0] != self.config.display_height:
                frame = self.frame_processor.resize_frame(
                    frame, self.config.display_width, self.config.display_height
                )
            
            # Store original frame
            with self.lock:
                self.original_frame = frame.copy()
            
            # Encode for gRPC
            encoded = self.frame_processor.encode_frame(frame)
            if encoded:
                yield detection_pb2.FrameRequest(
                    robot_id=robot_id,
                    timestamp=int(time.time() * 1000),
                    frame=encoded
                )
            else:
                logger.warning("Failed to encode frame, skipping")
            
            count += 1
    
    def _process_frames(self) -> None:
        """Process frames with the detection service in a background thread."""
        try:
            # Start streaming to the detection service
            response_stream = self.stub.StreamFrames(self._request_generator())
            
            # Process responses
            for response in response_stream:
                if not self.is_running:
                    break
                    
                if not response.annotated_frame:
                    logger.warning("Received empty response frame")
                    continue
                
                # Decode the annotated frame
                annotated_frame = self.frame_processor.decode_frame(response.annotated_frame)
                if annotated_frame is None:
                    logger.warning("Failed to decode annotated frame")
                    continue
                
                # Store annotated frame
                with self.lock:
                    self.annotated_frame = annotated_frame
                    self.detection_active = True
                
        except grpc.RpcError as e:
            logger.error(f"RPC error during streaming: {e.code()}: {e.details()}")
        except Exception as e:
            logger.exception(f"Error processing frames: {e}")
        finally:
            with self.lock:
                self.detection_active = False
    
    async def get_mjpeg_frame(self, annotated: bool = True) -> Optional[bytes]:
        """Get a MJPEG frame, either original or annotated."""
        try:
            with self.lock:
                if annotated and self.detection_active and self.annotated_frame is not None:
                    frame = self.annotated_frame.copy()
                elif self.original_frame is not None:
                    frame = self.original_frame.copy()
                else:
                    return None
            
            # Encode frame to JPEG
            encoded = self.frame_processor.encode_frame(frame)
            if encoded:
                return (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + encoded + b'\r\n')
            return None
        except Exception as e:
            logger.error(f"Error getting MJPEG frame: {e}")
            return None