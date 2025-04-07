import logging
from config import Config
from system import TrafficViolationSystem
import queue

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Main script started.")  # 
    try:
        config = Config()
        logging.info(f"Config loaded. image_source: {config.image_source}")  # 
        image_queue = queue.Queue(maxsize=1000)  # Create a queue
        logging.info("Queue created.")  # 
        system = TrafficViolationSystem(config, image_queue)
        logging.info("TrafficViolationSystem initialized.")  # 
        system.start()
        logging.info("System started.")  # 
    except Exception as e:
        logging.error(f"Exception in main: {e}")  # 