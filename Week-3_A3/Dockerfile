FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 3000

# Start the application
CMD ["uvicorn", "myapi:app", "--host", "0.0.0.0", "--port", "3000"]
