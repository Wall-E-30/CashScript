# Use official Python runtime
FROM python:3.10-slim

# Prevent Linux from pausing to ask for user input during installs
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install Tesseract safely
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy your project files into the container
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Render uses port 10000 by default
EXPOSE 10000

# Run the app using Gunicorn
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:10000"]