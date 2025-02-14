# Use an official Python image as base
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies before copying other files (this helps caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the FastAPI app correctly
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

RUN npm install -g prettier
