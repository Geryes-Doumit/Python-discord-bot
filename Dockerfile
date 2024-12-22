# Use the Python 3.10-bullseye base image
FROM python:3.10-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy your application code to the container
COPY ./ /app/

# update and install ffmpeg
RUN apt-get update && apt-get upgrade && apt-get install -y --fix-missing \
    ffmpeg \
    libsm6 \
    libxext6 \
    firefox-esr \
    libglib2.0-0 \
    libx11-xcb1 \
    libdbus-1-3 \
    libxt6 \
    libasound2 \
    libgdk-pixbuf2.0-0

# Install dependencies from a requirements.txt file
RUN pip install --no-cache-dir -r /app/requirements.txt

# Update the code in the container
RUN cd /app && git pull

# Define the command to run your application
CMD ["python", "-u", "/app/src/main.py"]
