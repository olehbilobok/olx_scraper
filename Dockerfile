# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file first to leverage Docker's cache for dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the entire app directory into the container
COPY app /app/

# Expose the port the app will run on (if applicable)
EXPOSE 80

# Set environment variable to make the app directory a Python package
ENV PYTHONPATH=/app

# Set the command to run the application
CMD ["python", "main.py"]
