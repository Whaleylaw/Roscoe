"""
Document Generation Handlers

This package contains handlers for different document types:
- docx_handler: Process DOCX templates with placeholder replacement
- markdown_handler: Convert Markdown to DOCX and PDF
- pdf_handler: Fill PDF form fields
"""

from .docx_handler import process_docx_template
from .markdown_handler import process_markdown_template
from .pdf_handler import process_pdf_form

__all__ = [
    'process_docx_template',
    'process_markdown_template',
    'process_pdf_form',
]

