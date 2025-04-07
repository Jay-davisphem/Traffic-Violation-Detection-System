import time
import datetime
import threading
import queue
import logging
from config import Config
from database import ViolationDatabase
from detector import ViolationDetector
from image_src import ImageSource

class TrafficViolationSystem:
    def __init__(self, config: Config, image_queue: queue.Queue):
        self.config = config
        self.db = ViolationDatabase(config.db_path)
        self.detector = ViolationDetector(config.gemini_api_key, config.image_dir, config.input_shape, config.prompt)
        self.image_source = ImageSource(config)
        self.running = False
        self.image_queue = image_queue
        self.process_thread = None
        logging.basicConfig(level=logging.INFO)

    def start(self):
        if self.running:
            return
        self.running = True
        self.image_source.start_capture(self.image_queue, self.db)  # Pass the queue and db to image source
        self.process_thread = threading.Thread(target=self.process_images)
        self.process_thread.daemon = True
        self.process_thread.start()
        logging.info("System started. Press Ctrl+C to stop.")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping system...")
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
                violation_type, violations = self.detector.detect_violation(image)
                if "Violation" in violation_type:
                    for violation in violations:
                        bbox_str = ",".join(map(str, violation['bbox']))
                        self.db.insert_violation(timestamp,
                                                 self.detector.save_violation_image(image, timestamp),
                                                 image_hash,  # Use the hash
                                                 violation['type'],
                                                 violation['confidence'],
                                                 bbox_str,
                                                 violation['position_description'],
                                                 )
                        logging.info(f"Violation logged: {violation['type']}, Confidence: {violation['confidence']}, BBox: {bbox_str}, Image: {timestamp}.jpg, Hash: {image_hash}")
                elif violation_type == "Error":
                    logging.error(f"Error processing image at {timestamp}")
                self.db.insert_image_hash(image_hash) #add this
                self.image_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing image: {e}")
                self.running = False
                break