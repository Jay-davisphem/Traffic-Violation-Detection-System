import google.generativeai as genai
import cv2
import os

def identify_image(api_key, image_path):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return None

    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image at {image_path}")
        return None

    _, encoded_image = cv2.imencode('.jpg', image)
    image_bytes = encoded_image.tobytes()

    prompt = """
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

    image_data = {
        'mime_type': 'image/jpeg',
        'data': image_bytes
    }

    try:
        response = model.generate_content([prompt, image_data])
        if response.text:
            return response.text
        else:
            print("Gemini API returned an empty response.")
            return None
    except Exception as e:
        print(f"Error during image identification: {e}")
        return None

if __name__ == "__main__":
    api_key = os.environ.get('GEMINI_API_KEY')
    image_path = 'data/image3.png'  

    result = identify_image(api_key, image_path)
    if result:
        print(f"Objects identified in the image:\n{result}")
    else:
        print("Failed to identify objects in the image.")

