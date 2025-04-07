# **Traffic Violation Detection System Documentation**


## **1. Project Overview**

The project is an AI-powered traffic violation detection system designed to identify traffic infractions, such as running red lights and unauthorized lane changes. The system uses a Raspberry Pi, a camera module, and machine learning-based image processing. Here's a detailed breakdown:


### **1.1 System Components:**



* **Raspberry Pi:** The central processing unit, responsible for running the application and coordinating the various system components. It was chosen for its low cost, small size, and ability to handle the necessary processing tasks.
* **Camera Module:** Captures images or video of traffic. The specific camera module was selected for its compatibility with the Raspberry Pi and its ability to provide sufficient image quality for accurate violation detection.
* **Software:** A Python-based application that captures images, detects violations, stores logs, and generates alerts. The application is designed to be modular and extensible, allowing for future enhancements and modifications.


### **1.2 Core Functionality:**



1. **Image Capturing:** The system captures images from a camera or reads them from a directory. The image capturing process is designed to be efficient and reliable, ensuring that images are captured at a sufficient frame rate and quality.
2. **Object Identification:** AI models analyze the images to detect traffic violations. The system employs state-of-the-art machine learning techniques to accurately identify violations, even in challenging conditions such as low light or adverse weather.
3. **Violation Logging:** Detected violations are stored in a database. The database provides a persistent record of all detected violations, allowing for later analysis and reporting.
4. **Alert Generation:** The system can generate alerts for detected violations, enabling further analysis or real-time responses. Alerts can be configured to be sent via email


## **2. System Architecture**

The project is divided into two main parts:


### **2.1 Image Capturing Part**



* **Description:** This part focuses on acquiring images for processing. It involves using either a camera or a directory of images as the source. The image capturing part is responsible for providing a steady stream of images to the object identification part.
* **Code Location:** The core logic for image capturing is located in image_src.py.
* **Key Components:**
    * ImageSource Class:
        * Initializes the image source (camera or directory).
        * Manages the capture process, including starting and stopping the capture thread.
        * Reads frames from the camera or images from a directory.
        * Handles saving captured frames to disk, if required.
        * Calculates image hashes to prevent processing duplicate images, ensuring that the system does not waste resources by analyzing the same image multiple times.
        * Uses a queue (image_queue) to pass captured images to the processing part. The queue allows for asynchronous processing, where image capturing and object identification can occur concurrently.
* **Workflow:**
    1. The ImageSource class is initialized with a configuration that specifies the image source (camera or directory), the capture frame rate, and other relevant parameters.
    2. The start_capture method is called, which starts a thread to continuously capture images. This thread runs in the background, allowing the main thread to focus on other tasks.
    3. If the source is a camera, cv2.VideoCapture is used to access the camera. The read_camera_frames method reads frames from the camera, saves them with a timestamp, calculates their hash, and puts them into a queue.
    4. If the source is a directory, the read_images_from_directory method reads each image from the directory, calculates its hash, and puts it into a queue.
    5. The stop_capture method stops the capture process and releases the camera resource, if applicable. This ensures that the camera is properly closed when the application is terminated.
    * The calculate_image_hash method calculates the MD5 hash of the image. This hash is used to quickly compare images and determine if they are duplicates.
* **File: image_src.py**
    * The ImageSource class encapsulates the image capturing logic.
    * The read_camera_frames function reads frames from a camera, saves the images, and puts them in a queue.
    * The read_images_from_directory function reads images from a directory and puts them in a queue.
    * The calculate_image_hash function calculates the hash of the image to avoid processing duplicates.
    * The start_capture and stop_capture methods control the capturing process.


### **2.2 Object Identification Part**



* **Description:** This part focuses on processing the captured images to detect traffic violations. It uses a pre-trained AI model (accessed via the Gemini API) to analyze the images. The object identification part is responsible for analyzing the images and identifying any violations.
* **Code Location:** The core logic for object identification is located in detector.py.
* **Key Components:**
    * ViolationDetector Class:
        * Initializes the AI model (Gemini).
        * Preprocesses images for the model, including resizing and normalizing the images.
        * Detects violations in the images using the AI model.
        * Saves images where violations were detected, along with the violation information.
        * Extracts relevant information about the violation (type, confidence, location) from the model's output.
* **Workflow:**
    1. The TrafficViolationSystem class (in system.py) retrieves images from the queue provided by the ImageSource class.
    2. The ViolationDetector class's detect_violation method is used to analyze the image.
    3. The preprocess_image method prepares the image for the AI model by resizing and normalizing it.
    4. The model.generate_content method sends the image to the Gemini API for analysis.
    5. The response from the API is parsed to extract violation information, such as the type of violation, the location of the violation in the image, and the confidence level of the detection.
    6. The save_violation_image method saves a copy of the image with the violation information for logging and further analysis.
    7. Violation details are then stored in the database.
* **File: detector.py**
    * The ViolationDetector class encapsulates the violation detection logic.
    * The preprocess_image function prepares the image for the AI model.
    * The detect_violation function uses the Gemini API to detect violations.
    * The save_violation_image function saves the image in case of a violation.


## **3. Multithreading Issues and Solutions**


### **3.1 The Issue**

The application uses multithreading to handle image capturing and processing concurrently. A key challenge in multithreaded applications is managing shared resources, such as database connections, to prevent race conditions and data corruption. Specifically, the original code faced potential issues with multiple threads trying to access the SQLite database simultaneously. SQLite, by default, has limited support for concurrent writes, which can lead to errors and performance bottlenecks.


### **3.2 The Solution**

To address this, I implemented thread-local database connections. Here's how it works:



* **Thread-Local Connections:** Instead of a single, shared connection, each thread now has its own connection to the database. This is achieved using threading.local(). Thread-local storage provides a way to store data that is specific to each thread.
* **Code Location:** The changes are primarily in the database.py file, within the ViolationDatabase class.
* **Implementation Details:**
    * A threading.local() object called self._local is created in the ViolationDatabase class. This object acts as a container for thread-specific data.
    * The _get_connection() and _get_cursor() methods now check if a connection/cursor exists for the *current* thread. If not, they create a new one and store it in the thread-local storage (self._local). This ensures that each thread has its own unique connection and cursor.
    * The close() method now closes only the connection associated with the *current* thread. This prevents one thread from accidentally closing the connection of another thread.
* **Benefits:**
    * **Concurrency:** Multiple threads can now safely interact with the database without interfering with each other. This significantly improves the performance and responsiveness of the application.
    * **Reduced Errors:** This eliminates the "database is locked" errors that can occur with concurrent access.
    * **Resource Management:** Connections are properly managed and closed on a per-thread basis, preventing resource leaks.


### **3.3 Code Example (database.py):**

import sqlite3 \
import threading \
from logger import logger \
 \
class ViolationDatabase: \
    def __init__(self, db_path): \
        self.db_path = db_path \
        self._local = threading.local()  # Thread-local storage \
        self.connect() \
        self.create_tables() \
 \
    def _get_connection(self): \
        if not hasattr(self._local, 'conn') or self._local.conn is None: \
            try: \
                self._local.conn = sqlite3.connect(self.db_path) \
                logger.info(f"Thread {threading.get_ident()}: Database connected.") \
            except sqlite3.Error as e: \
                logger.error(f"Thread {threading.get_ident()}: Error connecting to database: {e}") \
                raise \
        return self._local.conn \
 \
    # Similar changes in _get_cursor(), connect(), and close() \



## **4. Raspberry Pi Setup and Access**


### **4.1 Setting up Raspberry Pi for SSH Access**

To remotely access and manage the Raspberry Pi, we configured it for SSH (Secure Shell) access. This allows us to control the Raspberry Pi from a computer without needing a physical keyboard, mouse, and monitor connected to the Pi. Here's a detailed outline of the process:



1. **Enable SSH:**
    * On the Raspberry Pi, open the Raspberry Pi Configuration tool (either from the desktop or the command line using sudo raspi-config).
    * Navigate to "Interface Options" and enable SSH. This will allow the Raspberry Pi to accept incoming SSH connections.
    * Alternatively, you can create an empty file named ssh in the /boot/ directory of the SD card before booting the Raspberry Pi. This is useful for headless setups where you don't have a monitor connected to the Pi.
2. **Connect to the Network:**
    * Ensure the Raspberry Pi is connected to the same network as your computer, either via Ethernet or Wi-Fi. This is essential for establishing an SSH connection.
3. **Find the Raspberry Pi's IP Address:**
    * There are several ways to find the IP address:
        * Use the hostname -I command on the Raspberry Pi's terminal. This command will display the IP address(es) of the Raspberry Pi.
        * Check your router's administration interface for a list of connected devices. Most routers provide a web interface that shows the devices connected to the network, along with their IP addresses.
        * Use a network scanning tool on your computer, such as nmap.
4. **Connect via SSH:**
    * On your computer, open a terminal or SSH client (e.g., PuTTY on Windows).
    * Use the following command, replacing &lt;ip_address> with the Raspberry Pi's IP address: \
ssh pi@&lt;ip_address> \

    * The default username is "pi," and the default password is "raspberry." **It is crucial to change the default password for security reasons.** You can do this using the passwd command on the Raspberry Pi. A strong password will help to protect your Raspberry Pi from unauthorized access.


### **4.2 Cloning the Repository**

Once you have SSH access to the Raspberry Pi, you can clone the project repository:



1. **Open an SSH connection** to your Raspberry Pi.
2. **Navigate to the desired directory** where you want to store the project (e.g., your home directory): \
cd ~ \

3. **Clone the repository** using the git clone command: \
git clone https://github.com/Jay-davisphem/Traffic-Violation-Detection-System \
 \
(Replace with the actual repository URL)
4. **Navigate into the project directory:** \
cd Traffic-Violation-Detection-System \



### **4.3 Setting up the Environment and Running the Application**

Follow the instructions in the README.md file to set up the virtual environment, install the dependencies, and run the application. Remember to set the GEMINI_API_KEY environment variable as described in the README.md. This API key is required to access the Gemini AI model for object identification.
