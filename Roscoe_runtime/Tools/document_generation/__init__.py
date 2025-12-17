"""Document generation tools for the Roscoe paralegal agent."""

from .letterhead_generator import generate_letterhead_document
from .fill_pdf_form import fill_pdf_form, list_form_fields
from .medical_request_generator import generate_medical_request
from .template_filler import fill_template, list_templates, show_case_context
from .context_resolver import ContextResolver

__all__ = [
    'generate_letterhead_document',
    'fill_pdf_form',
    'list_form_fields',
    'generate_medical_request',
    'fill_template',
    'list_templates',
    'show_case_context',
    'ContextResolver'
]

