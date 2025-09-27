# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /workspace

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The command to run the function will be provided by the Functions Framework
# when we run the container. The entrypoint is set by docker-compose.
CMD ["functions-framework"]