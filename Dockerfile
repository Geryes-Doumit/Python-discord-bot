# Use the Python 3.10-bullseye base image
FROM python:3.10-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy your application code to the container
COPY ./ /app/

# Install dependencies from a requirements.txt file
RUN pip install --no-cache-dir -r /app/requirements.txt

# Define the command to run your application
CMD ["python", "/app/src/main.py"]
