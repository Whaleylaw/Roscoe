#!/usr/bin/env python3
"""
Test 7: Dependencies Check
Verifies that all expected Python packages are available in the Docker container.
"""

import sys

print("=" * 50)
print("Test: Dependencies Check")
print("=" * 50)

# List of packages that should be available
required_packages = [
    ("pandas", "Data analysis"),
    ("numpy", "Numerical computing"),
    ("pdfplumber", "PDF text extraction"),
    ("PyPDF2", "PDF manipulation"),
    ("requests", "HTTP client"),
    ("httpx", "Async HTTP client"),
    ("beautifulsoup4", "HTML parsing"),
    ("lxml", "XML/HTML parsing"),
    ("python-docx", "Word documents"),
    ("openpyxl", "Excel files"),
    ("markdown", "Markdown processing"),
    ("python-dateutil", "Date parsing"),
    ("jsonschema", "JSON validation"),
    ("loguru", "Logging"),
]

# Optional packages (nice to have)
optional_packages = [
    ("tavily", "Search API"),
    ("playwright", "Browser automation"),
    ("google.cloud.storage", "GCS client"),
]

print("\nRequired packages:")
all_required_found = True
for pkg_name, description in required_packages:
    try:
        # Handle packages with different import names
        import_name = pkg_name.replace("-", "_")
        if import_name == "beautifulsoup4":
            import_name = "bs4"
        elif import_name == "python_docx":
            import_name = "docx"
        elif import_name == "python_dateutil":
            import_name = "dateutil"
            
        __import__(import_name)
        print(f"  ✓ {pkg_name} ({description})")
    except ImportError as e:
        print(f"  ✗ {pkg_name} ({description}) - NOT FOUND: {e}")
        all_required_found = False

print("\nOptional packages:")
for pkg_name, description in optional_packages:
    try:
        import_name = pkg_name.replace("-", "_")
        __import__(import_name)
        print(f"  ✓ {pkg_name} ({description})")
    except ImportError:
        print(f"  - {pkg_name} ({description}) - not installed")

if all_required_found:
    print("\n✓ All required dependencies available!")
else:
    print("\n✗ Some required dependencies missing!")
    sys.exit(1)

