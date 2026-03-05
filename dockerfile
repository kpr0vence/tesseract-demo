# Use full Python image (not slim) to avoid missing dependencies
FROM python:3.12

# Set working directory
WORKDIR /app

# Install Tesseract OCR and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installed correctly
RUN tesseract --version

# Install Poetry for dependency management
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to install directly into the container environment
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

# Copy application code
COPY . .

# Expose the port
EXPOSE 8080

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]