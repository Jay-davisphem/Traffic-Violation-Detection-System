from logger import logger
from config import Config
from system import TrafficViolationSystem
import queue

if __name__ == "__main__":
    logger.info("Main script started.")  # 
    try:
        config = Config()
        logger.info(f"Config loaded. image_source: {config.image_source}")  # 
        image_queue = queue.Queue(maxsize=1000)  # Create a queue
        logger.info("Queue created.")  # 
        system = TrafficViolationSystem(config, image_queue)
        logger.info("TrafficViolationSystem initialized.")  # 
        system.start()
        logger.info("System started.")  # 
    except Exception as e:
        logger.error(f"Exception in main: {e}")  # 