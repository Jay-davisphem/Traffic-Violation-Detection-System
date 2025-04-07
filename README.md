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
    ##   Setting the GEMINI_API_KEY Environment Variable

    The application requires the `GEMINI_API_KEY` to access the Gemini API. You **must** set this as an environment variable before running the application.

    ###   Linux/macOS (Bash or Zsh)

    1.  **Open your terminal.**
    2.  **Execute the `export` command:**

        ```bash
        export GEMINI_API_KEY="YOUR_ACTUAL_API_KEY"
        ```

        * Replace `"YOUR_ACTUAL_API_KEY"` with the actual API key you obtained from Google.
        * `export` makes the variable available to the current terminal session and any processes run from it.

    3.  **Verify (Optional):**

        ```bash
        echo $GEMINI_API_KEY
        ```

        * This should print your API key to the terminal (be mindful of who can see your screen!).

    ###   Windows (Command Prompt)

    1.  **Open Command Prompt.**
    2.  **Execute the `set` command:**

        ```bash
        set GEMINI_API_KEY="YOUR_ACTUAL_API_KEY"
        ```

        * Replace `"YOUR_ACTUAL_API_KEY"` with your actual API key.
        * `set` makes the variable available for the current Command Prompt session.

    3.  **Verify (Optional):**

        ```bash
        echo %GEMINI_API_KEY%
        ```

    ###   Windows (PowerShell)

    1.  **Open PowerShell.**
    2.  **Execute the `$env:` assignment:**

        ```powershell
        $env:GEMINI_API_KEY = "YOUR_ACTUAL_API_KEY"
        ```

        * Replace `"YOUR_ACTUAL_API_KEY"` with your actual API key.

    3.  **Verify (Optional):**

        ```powershell
        echo $env:GEMINI_API_KEY
        ```

    ###   Important Details

    * **Terminal Session Scope:** Environment variables set this way are generally only available for the *current terminal session*. If you close the terminal, you'll need to set the variable again in a new terminal.
    * **Permanent Setting (Optional):**
        * **Linux/macOS:** To make the variable persistent across terminal sessions, you can add the `export` command to your shell's configuration file (e.g., `~/.bashrc`, `~/.bash_profile`, or `~/.zshrc`).
        * **Windows:** You can set permanent environment variables through the System Properties or Environment Variables settings in the Control Panel. However, for security reasons, it's often better to set them only when needed.
    * **Security Best Practice:** Never hardcode your API key directly into your Python scripts! Environment variables are a much safer way to handle sensitive credentials.
    * **Obtaining the API Key:** Ensure you have obtained a valid `GEMINI_API_KEY` from Google. The application will not function without it.

    Execute the `main.py` script using Python:

    ```bash
    python main.py
    ```

    * If your system has both python2 and python3, and python3 is not the default, you may have to run:
    ```bash
    python3 main.py
    ```
