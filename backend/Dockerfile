# Use Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Expose backend port
EXPOSE 5000

# Run the backend server (Flask example)
CMD ["python", "recommender.py"]