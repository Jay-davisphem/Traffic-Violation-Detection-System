# Python Application Setup and Running Instructions

This document provides instructions on how to set up and run the Python application located in this directory.

## Prerequisites

* Python 3.6 or higher installed on your system.
* `pip` (Python package installer) installed.
* It's also helpful to have sqlite3 installed on your system, there's a high prob that you have it.

## Setup

1.  **Clone the Repository (if applicable):**

    If you downloaded this application from a repository (e.g., GitHub), clone it to your local machine:

    ```bash
    git clone https://github.com/Jay-davisphem/Traffic-Violation-Detection-System
    cd Traffic-Violation-Detection-System
    ```

2.  **Create a Virtual Environment (Recommended):**

    It's highly recommended to create a virtual environment to isolate the application's dependencies. This prevents conflicts with other Python projects.

    ```bash
    python3 -m venv venv
    ```

    * On Windows:

        ```bash
        venv\Scripts\activate
        ```

    * On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

3.  **Install Dependencies:**

    Install the required Python packages listed in `requirements.txt` using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Navigate to the Application Directory:**

    Ensure you are in the directory containing `main.py`.

2.  **Run the Application:**

    Execute the `main.py` script using Python:

    ```bash
    python main.py
    ```

    * If your system has both python2 and python3, and python3 is not the default, you may have to run:
    ```bash
    python3 main.py
    ```