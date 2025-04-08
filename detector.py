import cv2
import numpy as np
import os
import json
import google.generativeai as genai
from logger import logger
import re

class ViolationDetector:
    def __init__(self, api_key, image_dir, input_shape, prompt, model):
        self.api_key = api_key
        self.image_dir = image_dir
        self.input_shape = input_shape
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model) # final descision is gemini-2.5-pro-exp-03-25
        self.prompt = prompt
        logger.info("ViolationDetector initialized.")

    def preprocess_image(self, image):
        try:
            resized_image = cv2.resize(image, self.input_shape)
            logger.debug("Image preprocessed successfully.")
            return resized_image.astype(np.uint8)
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None

    def detect_violation(self, image):
        preprocessed_image = self.preprocess_image(image)
        if preprocessed_image is None:
            return "Error", []
        try:
            _, encoded_image = cv2.imencode('.jpg', preprocessed_image)
            image_bytes = encoded_image.tobytes()
            image_data = {'mime_type': 'image/jpeg', 'data': image_bytes}
            response = self.model.generate_content(
                [self.prompt, image_data],
                generation_config=genai.GenerationConfig()
            )
            if response.text is None:
                logger.warning("Gemini API returned an empty response.")
                return "Error", []
            # Remove ```json and ``` from the response text
            cleaned_response = re.sub(r'```json|```', '', response.text).strip()
            try:
                results = json.loads(cleaned_response)
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON response: {cleaned_response}")
                return "Error", []
            violations = results.get('violations', [])
            logger.info(f"Detections received: {violations}")
            if not violations:
                return "no_violation", []
            return "Violation", violations
        except Exception as e:
            logger.error(f"Error detecting violation: {e}")
            return "Error", []

    def save_violation_image(self, image, timestamp):
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        filename = f"{timestamp}.jpg"
        image_path = os.path.join(self.image_dir, filename)
        try:
            cv2.imwrite(image_path, image)
            logger.info(f"Violation image saved: {image_path}")
            return image_path
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return None
