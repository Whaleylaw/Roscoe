# Roscoe Python Script Runner
# Base image for executing /Tools/ scripts with GCS filesystem access

FROM python:3.11-slim

LABEL maintainer="Roscoe Paralegal Agent"
LABEL description="Python script execution environment with GCS filesystem access"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    gcc \
    g++ \
    # Version control
    git \
    # Network tools
    curl \
    wget \
    # File type detection
    libmagic1 \
    # PDF processing dependencies
    poppler-utils \
    # OCR support (for document processing)
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages commonly used in Tools scripts
RUN pip install --no-cache-dir \
    # Core data processing
    pandas==2.1.4 \
    numpy==1.26.2 \
    # PDF processing
    PyPDF2==3.0.1 \
    pdfplumber==0.10.3 \
    pypdf==3.17.4 \
    pytesseract==0.3.10 \
    pdf2image==1.16.3 \
    # Document processing
    python-docx==1.1.0 \
    openpyxl==3.1.2 \
    # Internet and APIs
    requests==2.31.0 \
    httpx==0.25.2 \
    beautifulsoup4==4.12.2 \
    lxml==4.9.3 \
    # Legal/Medical research APIs
    tavily-python==0.3.0 \
    biopython==1.83 \
    # Markdown and text processing
    markdown==3.5.1 \
    markdownify==0.11.6 \
    # Date/time parsing
    python-dateutil==2.8.2 \
    # JSON processing
    jsonschema==4.20.0 \
    # File operations
    python-magic==0.4.27 \
    # Logging and utilities
    loguru==0.7.2 \
    # Playwright (browser automation - browsers installed separately)
    playwright==1.40.0 \
    # Google Cloud Storage (for direct API access if needed)
    google-cloud-storage==2.14.0 \
    # Airtable integration
    pyairtable==2.2.1

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash roscoe && \
    mkdir -p /home/roscoe/.cache && \
    chown -R roscoe:roscoe /home/roscoe

# Set working directory
WORKDIR /workspace

# Switch to non-root user
USER roscoe

# Set Python to unbuffered mode for immediate output
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command (will be overridden)
CMD ["python", "--version"]

