# Roscoe Agents Docker Image
#
# This image extends the LangGraph API server with all Roscoe dependencies.
# Build: docker build -t roscoe-agents:local -f docker/roscoe-agents/Dockerfile .
# Run: See docker-compose.yml
#
# The image:
# 1. Starts from LangGraph's official server image
# 2. Installs system dependencies (for PDF processing, etc.)
# 3. Installs Python dependencies from pyproject.toml
# 4. Mounts source code at runtime (no rebuild needed for code changes)

FROM langchain/langgraph-api:3.11

# Set working directory
WORKDIR /deps/Roscoe

# Install system dependencies for PDF processing, image handling, etc.
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PDF processing
    poppler-utils \
    # OCR support
    tesseract-ocr \
    # Image processing
    libgl1 \
    libglib2.0-0 \
    # Build tools for some Python packages
    build-essential \
    # Git for pip installs from git repos
    git \
    # LibreOffice for DOCX to PDF conversion (document templates)
    libreoffice-writer \
    libreoffice-common \
    && rm -rf /var/lib/apt/lists/*

# Copy only pyproject.toml first for better caching
COPY pyproject.toml .

# Install Python dependencies from pyproject.toml
# Using pip install . with --no-deps for the package itself (source mounted at runtime)
# Then installing all dependencies explicitly
RUN pip install --no-cache-dir \
    # Core agent framework
    "deepagents>=0.2.0" \
    # LangChain ecosystem
    langchain \
    langgraph \
    "langgraph-cli[inmem]" \
    langchain-anthropic \
    langchain-google-genai \
    langchain-openai \
    langchain-community \
    langchain-experimental \
    # Research
    tavily-python \
    # NLP/ML
    sentence-transformers \
    # PDF processing
    pdfplumber \
    PyPDF2 \
    pypdf \
    reportlab \
    pdf2image \
    pytesseract \
    # Data processing
    pandas \
    numpy \
    # Integrations
    slack-sdk \
    slack-bolt \
    python-dotenv \
    "docker>=7.0.0" \
    # String matching
    rapidfuzz \
    # UI integration
    copilotkit \
    fastapi \
    uvicorn \
    # APIs
    openai \
    google-cloud-storage \
    "langchain-google-community[gmail]" \
    "google-auth-oauthlib>=1.2.0" \
    "google-api-python-client>=2.100.0" \
    # Document processing
    openpyxl \
    python-docx \
    defusedxml \
    pillow \
    pyyaml \
    markitdown \
    # Knowledge graph
    "graphiti-core[falkordb,google-genai]>=0.24.0" \
    # Physical mail API
    "lob>=4.5.0"

# Copy langgraph.json for the LangGraph server
COPY langgraph.json .

# Copy the entrypoint script
COPY docker/roscoe-agents/entrypoint.sh /storage/entrypoint.sh
RUN chmod +x /storage/entrypoint.sh

# Source code is mounted at runtime via docker-compose volumes:
# /home/aaronwhaley/roscoe/src/roscoe:/deps/Roscoe/src/roscoe
# This allows code changes without rebuilding the image.

# The LangGraph server expects code at /deps/Roscoe/src/roscoe
# which maps to the graphs defined in langgraph.json

# Set Python path to find the mounted source
ENV PYTHONPATH="/deps/Roscoe/src:${PYTHONPATH}"

# Expose the LangGraph API port
EXPOSE 8000

# Use custom entrypoint that sets up environment and starts LangGraph server
ENTRYPOINT ["/storage/entrypoint.sh"]
