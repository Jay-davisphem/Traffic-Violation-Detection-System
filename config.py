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
            Detect traffic violations in the image.  Identify the type of violation,
            and provide bounding box coordinates (x1, y1, x2, y2) for the violating vehicle.
            Possible violation types are: "wrong_way", "clearway", "red_light", "speeding", "lane_change".
            If no violation is detected, return "no_violation".
            
            Respond with a JSON object.  The JSON object should have the following structure:
            
            {
                "violations": [
                    {
                        "type": "violation_type",
                        "bbox": [x1, y1, x2, y2],
                        "position_description": "very detailed description of where visually",
                        "confidence": confidence_score
                    },
                    ... // more violations if any
                ]
            }
            
            Example 1:
            {
                "violations": [
                    {
                        "type": "red_light",
                        "bbox": [100, 200, 300, 400],
                        "position_description": "",
                        "confidence": 0.95
                    }
                ]
            }
            
            Example 2:
            {
                "violations": [
                    {
                        "type": "wrong_way",
                        "bbox": [50, 100, 150, 200],
                        "position_description": "",
                        "confidence": 0.88
                    },
                    {
                        "type": "speeding",
                        "bbox": [250, 300, 350, 400],
                        "position_description": "",
                        "confidence": 0.75
                    }
                ]
            }
            
            Example 3:
            {
                "violations": []
            }
            """
            
        logger.info(f"Config initialized with image_source: {self.image_source}")