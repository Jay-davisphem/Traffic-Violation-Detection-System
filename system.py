import time
import threading
import queue
from logger import logger
from config import Config
from database import ViolationDatabase
from detector import ViolationDetector
from image_src import ImageSource
import os

GEMINI_API_MODEL = os.environ.get('GEMINI_API_MODEL', 'gemini-2.0-flash') or 'gemini-2.0-flash'
class TrafficViolationSystem:
    def __init__(self, config: Config, image_queue: queue.Queue):
        self.config = config
        self.db = ViolationDatabase(config.db_path)
        self.detector = ViolationDetector(config.gemini_api_key, config.image_dir, config.input_shape, config.prompt, GEMINI_API_MODEL)
        self.image_source = ImageSource(config)
        self.running = False
        self.image_queue = image_queue
        self.process_thread = None

    def start(self):
        if self.running:
            logger.info("System already running.")
            return
        self.running = True
        logger.info("Image capture started affirmed")
        self.image_source.start_capture(self.image_queue, self.db)
        logger.info("Image capture started., was here")
        self.process_thread = threading.Thread(target=self.process_images)
        self.process_thread.daemon = True
        self.process_thread.start()
        logger.info(f"Process thread started: {self.process_thread.is_alive()}") # Check if thread is alive 
        logger.info("System started. Press Ctrl+C to stop.")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping system...")
            self.stop()
        finally:
            self.cleanup()

    def stop(self):
        self.running = False
        if self.process_thread:
            self.process_thread.join()
        self.image_source.stop_capture()
        self.db.close()

    def cleanup(self):
        self.image_source.stop_capture()
        self.db.close()

    def process_images(self):
        while self.running:
            try:
                image, timestamp, image_hash = self.image_queue.get(timeout=1)
                if image is None:
                    continue
                violation_type, violations = self.detector.detect_and_notify(image, timestamp, image_hash) # detect_and_notify by email
                if "Violation" in violation_type:
                    for violation in violations:
                        bbox_str = ",".join(map(str, violation['bbox']))
                        self.db.insert_violation(timestamp,
                                             self.detector.save_violation_image(image, timestamp),
                                             image_hash,
                                             violation['type'],
                                             violation['confidence'],
                                             bbox_str,
                                             violation['position_description'],
                                             )
                        logger.info(f"Violation logged: {violation['type']}, Confidence: {violation['confidence']}, BBox: {bbox_str}, Image: {timestamp}.jpg, Hash: {image_hash}")
                elif violation_type == "Error":
                    logger.error(f"Error processing image at {timestamp}")

                self.image_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                self.running = False
                break
        logger.info("Process images thread stopped.")
