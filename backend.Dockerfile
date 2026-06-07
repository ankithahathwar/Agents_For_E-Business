FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies first (leveraging Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Run Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
