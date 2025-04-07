import logging
from config import Config
from system import TrafficViolationSystem
import queue

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = Config()
    image_queue = queue.Queue(maxsize=1000)  # Create a queue
    system = TrafficViolationSystem(config, image_queue)
    system.start()