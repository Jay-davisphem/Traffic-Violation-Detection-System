import datetime
import queue
import os
import cv2
import logging
from config import Config
import threading
import time
import hashlib

class ImageSource:
    def __init__(self, config: Config):
        self.source_type = config.image_source
        self.camera_index = config.camera_index
        self.config = config
        self.read_images_thread = None
        self.running = False
        self.image_queue = None  # Will be set in start_capture
        self.db = None
        logging.info(f"ImageSource initialized with type: {self.source_type}")

    def start_capture(self, image_queue, db):
        """Start capturing images, either from camera or directory."""
        self.image_queue = image_queue
        self.running = True
        self.db = db
        logging.info("Capture started.")
        if self.source_type == "camera":
            self.capture = cv2.VideoCapture(self.camera_index)
            if not self.capture.isOpened():
                logging.error(f"Error: Unable to open camera with index {self.camera_index}")
                self.running = False  # Stop if camera can't be opened
                return
            self.read_camera_frames()  # Start reading frames directly in this thread
        elif self.source_type == "data":
            # Start the thread to read images from the directory
            self.read_images_thread = threading.Thread(target=self.read_images_from_directory)
            self.read_images_thread.daemon = True
            self.read_images_thread.start()
        else:
            logging.error("Invalid source type. Please check the config.")
            self.running = False

    def stop_capture(self):
        """Stop image capture."""
        logging.info("Capture stopped.")
        self.running = False
        if self.source_type == "camera":
            if hasattr(self, 'capture') and self.capture is not None:  # Check if capture is defined
                self.capture.release()
        elif self.source_type == "data":
            if self.read_images_thread is not None:
                self.read_images_thread.join()  # Wait for thread to finish
        self.image_queue = None
        self.db = None

    def read_camera_frames(self):
        """Reads frames from the camera and puts them in the queue."""
        while self.running:
            ret, frame = self.capture.read()
            if not ret or frame is None:
                logging.warning("Failed to capture frame from camera.")
                time.sleep(0.1)  # sleep to prevent high CPU usage
                continue
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                self.image_queue.put((frame, timestamp), block=True, timeout=1)
            except queue.Full:
                logging.warning("Queue is full. Skipping frame.")

    def read_images_from_directory(self):
        """Reads images from the directory, checks hash, and puts them in the queue."""
        image_dir = self.config.image_source
        image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        logging.info(f"Found {len(image_files)} image files in {image_dir}")
        while self.running:
            for image_file in image_files:
                if not self.running:
                    break
                image_path = os.path.join(image_dir, image_file)
                image_hash = self.calculate_image_hash(image_path)
                if not self.db.check_image_hash(image_hash):
                    logging.info(f"Reading image: {image_path}")
                    frame = cv2.imread(image_path)
                    if frame is None:
                        logging.error(f"Failed to read image {image_path}")
                        continue
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    try:
                        self.image_queue.put((frame, timestamp, image_hash), block=True, timeout=1)
                        logging.info(f"Image added to queue: {image_path}")
                    except queue.Full:
                        logging.warning("Queue is full. Skipping image.")
                    time.sleep(0.1)  # Add a small delay to control reading speed
                else:
                    logging.info(f"Image already processed: {image_path}, hash: {image_hash}")
                    continue # add continue here
            time.sleep(60) #rescan every 5 seconds
        logging.info("Finished reading images from directory.")

    def calculate_image_hash(self, image_path):
        """Calculate the MD5 hash of the image file."""
        hasher = hashlib.md5()
        try:
            with open(image_path, 'rb') as image_file:
                buf = image_file.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logging.error(f"Error calculating image hash for {image_path}: {e}")
            return None

    def read_frame(self):
        """Reads a frame from the current source (camera or directory)."""
        if self.source_type == 'camera':
            ret, frame = self.capture.read()
            if ret:
                return frame, True
            else:
                return None, False
        return None, False #shouldn't be called
    
    def get_latest_frame(self):
        """Returns the latest frame from the active camera."""
        if self.source_type != 'camera' or not hasattr(self, 'capture'):
            return None, False
        return self.capture.read()

        