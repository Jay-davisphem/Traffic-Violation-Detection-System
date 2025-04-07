# Use a base image that supports ARMv7
FROM amd64/debian:bullseye

# Set the working directory in the container
WORKDIR /app

# Install essential tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    libopencv-dev \  
    libatlas-base-dev \ 
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (you'll add more later)
COPY requirements.txt .  

RUN pip3 install -r requirements.txt

# Copy your application code
COPY . /app

# Optional: Expose a port if your application needs it
# EXPOSE 5000

# Command to run when the container starts
# CMD ["python3", "app.py"]
