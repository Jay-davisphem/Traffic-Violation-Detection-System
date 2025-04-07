import os
from logger import logger

class Config:
    def __init__(self):
        self.image_source = "camera"
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.violation_threshold = 0.5
        self.image_dir = "violations"
        self.db_path = "violations.db"
        self.camera_index = 0
        self.input_shape = (256, 256)
        self.prompt = """
            You are given an image from a traffic surveillance system.

            Your task is to:
            1. Detect any traffic violations present in the image.
            2. Identify the type of violation.
            3. Return bounding box coordinates for each violating vehicle in the format [x1, y1, x2, y2].
            4. Include a **very detailed visual description** of where each violating vehicle is located within the image.
            5. Provide a confidence score (0.0 to 1.0) for each violation.

            Possible traffic violation types include (but are not limited to):
            - "red_light": Vehicle crossing an intersection while the traffic light is red.
            - "wrong_way": Vehicle driving in the opposite direction of the lane or road.
            - "unauthorized_lane_change": Vehicle switching lanes illegally (e.g., solid line crossing).
            - "speeding": Vehicle moving faster than the posted speed limit.
            - "clearway_violation": Vehicle parked or stopped in a designated clearway zone.
            - "no_parking_zone": Vehicle parked in an area marked as no parking.
            - "stop_sign_violation": Vehicle failing to stop at a stop sign.
            - "pedestrian_crossing_violation": Vehicle encroaching on or not yielding to a pedestrian crossing.
            - "illegal_turn": Vehicle making a prohibited U-turn or turning where it’s not allowed.
            - "lane_straddling": Vehicle positioned across multiple lanes improperly.
            - "bus_lane_violation": Unauthorized vehicle driving in a bus-only lane.

            If **no violation** is detected, return `"violations": []`.

            Respond strictly in a valid JSON format as shown below:

            {
                "violations": [
                    {
                        "type": "violation_type",
                        "bbox": [x1, y1, x2, y2],
                        "position_description": "very detailed description of where the vehicle is located in the image",
                        "confidence": float (e.g., 0.92)
                    },
                    ...
                ]
            }

            ### Example 1 (single violation):
            {
                "violations": [
                    {
                        "type": "red_light",
                        "bbox": [100, 200, 300, 400],
                        "position_description": "The red car is in the middle of the intersection, clearly beyond the white stop line under an active red light",
                        "confidence": 0.95
                    }
                ]
            }

            ### Example 2 (multiple violations):
            {
                "violations": [
                    {
                        "type": "wrong_way",
                        "bbox": [50, 100, 150, 200],
                        "position_description": "A black SUV is traveling in the wrong direction on a one-way street marked by white arrows pointing the opposite way",
                        "confidence": 0.88
                    },
                    {
                        "type": "speeding",
                        "bbox": [250, 300, 350, 400],
                        "position_description": "A silver sedan in the left lane appears blurred and ahead of other vehicles, suggesting high speed in a clearly marked 40 km/h zone",
                        "confidence": 0.78
                    }
                ]
            }

            ### Example 3 (no violations):
            {
                "violations": []
            }
            """

            
        logger.info(f"Config initialized with image_source: {self.image_source}")