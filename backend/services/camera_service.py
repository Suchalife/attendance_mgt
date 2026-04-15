"""
Camera Service for handling webcam operations
Simple service for capturing and streaming video frames
"""
import cv2
import time


class CameraService:
    """Service for camera operations"""
    
    def __init__(self):
        self.camera = None
        self.is_streaming = False
    
    def start_camera(self, camera_id=0):
        """
        Initialize camera
        Args:
            camera_id: Camera device ID (default 0 for primary webcam)
        Returns:
            bool: True if camera started successfully
        """
        try:
            if self.camera is not None:
                print("Camera already initialized")
                return True
            
            self.camera = cv2.VideoCapture(camera_id)
            
            if not self.camera.isOpened():
                print(f"Failed to open camera {camera_id}")
                self.camera = None
                return False
            
            # Set camera properties for better quality
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 15)
            
            self.is_streaming = True
            print(f"Camera {camera_id} started successfully")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            self.camera = None
            return False
    
    def stop_camera(self):
        """
        Release camera resources
        Returns:
            bool: True if camera stopped successfully
        """
        try:
            self.is_streaming = False
            
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                print("Camera stopped and released")
            
            return True
            
        except Exception as e:
            print(f"Error stopping camera: {e}")
            return False
    
    def get_frame(self):
        """
        Capture single frame from camera
        Returns:
            bytes: JPEG encoded frame, or None if failed
        """
        if self.camera is None or not self.camera.isOpened():
            print("Camera not initialized")
            return None
        
        try:
            ret, frame = self.camera.read()
            
            if not ret:
                print("Failed to capture frame")
                return None
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            if not ret:
                print("Failed to encode frame")
                return None
            
            return buffer.tobytes()
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def generate_frames(self):
        """
        Generator function for MJPEG streaming
        Yields frames in multipart format
        """
        # Ensure camera is started
        if self.camera is None:
            if not self.start_camera():
                return
        
        frame_count = 0
        
        while self.is_streaming:
            frame_bytes = self.get_frame()
            
            if frame_bytes is None:
                # If frame capture fails, try to restart camera
                print("Frame capture failed, attempting to restart camera...")
                self.stop_camera()
                time.sleep(1)
                if not self.start_camera():
                    break
                continue
            
            frame_count += 1
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Limit frame rate to ~15 FPS
            time.sleep(0.066)  # ~66ms delay
        
        print(f"Streaming stopped. Total frames: {frame_count}")
    
    def is_camera_active(self):
        """
        Check if camera is active
        Returns:
            bool: True if camera is active
        """
        return self.camera is not None and self.camera.isOpened()


# Global camera service instance
camera_service = CameraService()
