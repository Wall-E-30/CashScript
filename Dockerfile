# Use the full Python 3.10 image (no 'slim' tag) for guaranteed apt-get stability
FROM python:3.10

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install only the exact Tesseract packages needed
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng

# Set the working directory
WORKDIR /app

# Copy your project files into the container
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Render's default port
EXPOSE 10000

# Run the app using Gunicorn
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:10000"]