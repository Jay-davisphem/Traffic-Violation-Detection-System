import cv2
import numpy as np
import os
import json
import google.generativeai as genai
from logger import logger
import re
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

GMAIL_APP_PASS = os.environ.get('GMAIL_APP_PASS')
GMAIL_USER = os.environ.get('GMAIL_USER', 'davidoluwafemi178@gmail.com')
GMAIL_R_USER = os.environ.get('GMAIL_USER', 'davidoluwafemi178@gmail.com')

class ViolationDetector:
    def __init__(self, api_key, image_dir, input_shape, prompt, model):
        self.api_key = api_key
        self.image_dir = image_dir
        self.input_shape = input_shape
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model) # final descision is gemini-2.5-pro-exp-03-25
        self.prompt = prompt
        self.sender_email = GMAIL_USER
        self.sender_password = GMAIL_APP_PASS 
        self.recipient_email = GMAIL_R_USER
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

    def send_violation_alert(self, recipient_email, violation_details, image_path):
        """Sends an email alert for a detected traffic violation."""
        subject = "Traffic Violation Alert"
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        text = f"A traffic violation has been detected:\n\n{violation_details}"
        msg.attach(MIMEText(text, 'plain'))

        # Attach the image
        try:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                image = MIMEBase('image', 'jpg')
                image.set_payload(img_data)
                encoders.encode_base64(image)
                image.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(image_path)}"')
                msg.attach(image)
        except Exception as e:
            print(f"Error attaching image: {e}")
            logger.error(f"Error attaching image: {e}")

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # Use Gmail's SMTP server
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
            print(f"Email sent to {recipient_email}")
            logger.info(f"Email sent to {recipient_email}")
        except Exception as e:
            print(f"Error sending email: {e}")
            logger.error(f"Error sending email: {e}")

    def detect_and_notify(self, image, timestamp, image_hash):
        """Detects violations and sends email if any are found."""
        violation_type, violations = self.detect_violation(image)
        if "Violation" in violation_type:
            for violation in violations:
                bbox_str = ",".join(map(str, violation['bbox']))
                image_path = self.save_violation_image(image, timestamp)
                logger.info(
                    f"Violation logged: {violation['type']}, Confidence: {violation['confidence']}, BBox: {bbox_str}, Image: {timestamp}.jpg, Hash: {image_hash}")
                # Send email alert
                violation_details = (
                    f"Type: {violation['type']}\n"
                    f"Location: {violation['position_description']}\n"
                    f"Time: {timestamp}\n"
                    f"Confidence: {violation['confidence']}\n"
                    f"Bounding Box: {bbox_str}"
                )
                self.send_violation_alert(self.recipient_email, violation_details, image_path)
        elif violation_type == "Error":
            logger.error(f"Error processing image at {timestamp}")
        return violation_type, violations 
