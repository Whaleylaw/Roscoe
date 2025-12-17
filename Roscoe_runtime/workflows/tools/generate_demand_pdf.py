#!/usr/bin/env python3
"""
Demand Letter PDF Generator

Converts a filled markdown demand template into a professional PDF
matching the Whaley Law Firm format, with exhibits attached.

Usage:
    python generate_demand_pdf.py --input filled_demand.md --output demand_packet.pdf

Dependencies:
    pip install reportlab pypdf pyyaml Pillow markdown
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from pypdf import PdfReader, PdfWriter


# =============================================================================
# Configuration Loading
# =============================================================================

def load_firm_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load firm configuration from JSON file."""
    if config_path is None:
        # Default to same directory as this script
        script_dir = Path(__file__).parent
        config_path = script_dir / "firm_config.json"
    
    with open(config_path, 'r') as f:
        return json.load(f)


# =============================================================================
# Markdown Parsing
# =============================================================================

def parse_demand_markdown(md_path: str) -> Dict[str, Any]:
    """
    Parse the demand markdown template into structured data.
    
    Returns dict with:
        - metadata: YAML frontmatter values
        - sections: Dict of section name -> content
        - photos: List of (caption, path) tuples
        - exhibits: List of (description, path) tuples
        - tables: Dict of table name -> list of rows
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        'metadata': {},
        'sections': {},
        'photos': [],
        'exhibits': [],
        'tables': {}
    }
    
    # Extract YAML frontmatter
    yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if yaml_match:
        try:
            result['metadata'] = yaml.safe_load(yaml_match.group(1))
        except yaml.YAMLError as e:
            print(f"Warning: Could not parse YAML frontmatter: {e}")
        content = content[yaml_match.end():]
    
    # Remove HTML comments (instructions)
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Extract photos: ![Caption](path)
    photo_pattern = r'!\[(.*?)\]\((.*?)\)'
    for match in re.finditer(photo_pattern, content):
        caption, path = match.groups()
        if path and not path.startswith('http'):
            result['photos'].append((caption, path))
    
    # Extract exhibits: Number. Description | /path/to/file.pdf
    exhibit_pattern = r'^\d+\.\s*(.*?)\s*\|\s*(.+\.pdf)\s*$'
    for match in re.finditer(exhibit_pattern, content, re.MULTILINE):
        description, path = match.groups()
        result['exhibits'].append((description.strip(), path.strip()))
    
    # Parse main sections
    section_pattern = r'^#\s+([A-Z &]+)\s*$'
    sections = re.split(section_pattern, content, flags=re.MULTILINE)
    
    # sections[0] is content before first section (ignore)
    # Then alternating: section_name, section_content, section_name, section_content...
    i = 1
    while i < len(sections) - 1:
        section_name = sections[i].strip()
        section_content = sections[i + 1].strip()
        result['sections'][section_name] = section_content
        i += 2
    
    # Parse tables within sections
    for section_name, section_content in result['sections'].items():
        tables = parse_markdown_tables(section_content)
        if tables:
            result['tables'][section_name] = tables
    
    return result


def parse_markdown_tables(content: str) -> List[List[List[str]]]:
    """
    Parse markdown tables from content.
    Returns list of tables, each table is list of rows, each row is list of cells.
    """
    tables = []
    
    # Find table blocks (lines starting with |)
    lines = content.split('\n')
    current_table = []
    in_table = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('|') and line.endswith('|'):
            # Skip separator rows (|---|---|)
            if re.match(r'^\|[\s\-:|]+\|$', line):
                continue
            # Parse table row
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            current_table.append(cells)
            in_table = True
        else:
            if in_table and current_table:
                tables.append(current_table)
                current_table = []
            in_table = False
    
    # Don't forget last table
    if current_table:
        tables.append(current_table)
    
    return tables


def parse_provider_blocks(content: str) -> List[Dict[str, Any]]:
    """
    Parse provider treatment blocks from Treatment Chronology section.
    
    Format:
    ### Provider Name
    - **Treatment Timeline**: dates
    - **Number of Visits**: X
    - **Summary**:
      - bullet points
    - **Supporting Documents**: Exhibit X
    """
    providers = []
    
    # Split by ### headers
    blocks = re.split(r'^###\s+', content, flags=re.MULTILINE)
    
    for block in blocks[1:]:  # Skip content before first ###
        if not block.strip():
            continue
        
        lines = block.strip().split('\n')
        provider_name = lines[0].strip()
        
        provider = {
            'name': provider_name,
            'timeline': '',
            'visits': '',
            'summary': [],
            'exhibit': ''
        }
        
        current_field = None
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('- **Treatment Timeline**:'):
                provider['timeline'] = line.split(':', 1)[1].strip()
            elif line.startswith('- **Number of Visits**:'):
                provider['visits'] = line.split(':', 1)[1].strip()
            elif line.startswith('- **Summary**:'):
                current_field = 'summary'
            elif line.startswith('- **Supporting Documents**:'):
                provider['exhibit'] = line.split(':', 1)[1].strip()
                current_field = None
            elif current_field == 'summary' and line.startswith('-'):
                provider['summary'].append(line[1:].strip())
        
        providers.append(provider)
    
    return providers


# =============================================================================
# PDF Generation
# =============================================================================

class DemandDocTemplate(BaseDocTemplate):
    """Custom document template with letterhead."""
    
    def __init__(self, filename, config: Dict[str, Any], **kwargs):
        self.config = config
        super().__init__(filename, pagesize=letter, **kwargs)
        
        # Define frames
        frame = Frame(
            self.leftMargin, 
            self.bottomMargin,
            self.width,
            self.height,
            id='normal'
        )
        
        # Page templates
        self.addPageTemplates([
            PageTemplate(id='First', frames=frame, onPage=self._first_page_header),
            PageTemplate(id='Later', frames=frame, onPage=self._later_page_header),
        ])
    
    def _first_page_header(self, canvas, doc):
        """Draw letterhead on first page matching Whaley Law Firm format."""
        canvas.saveState()
        
        firm = self.config.get('firm', {})
        attorney = self.config.get('attorney', {})
        contact = self.config.get('contact', {})
        
        # Logo (left side) - Use the actual firm logo image
        logo_path = firm.get('logo_path', '')
        logo_width = 3.5 * inch  # Scale to 3.5 inches wide
        logo_height = logo_width / 3.45  # Maintain aspect ratio (3.45:1)
        logo_y = letter[1] - 0.4*inch - logo_height  # Position from top
        
        if logo_path and os.path.exists(logo_path):
            try:
                canvas.drawImage(logo_path, inch, logo_y, 
                                width=logo_width, height=logo_height,
                                preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Warning: Could not draw logo: {e}")
                self._draw_whaley_logo(canvas, inch, letter[1] - 0.5*inch)
        else:
            self._draw_whaley_logo(canvas, inch, letter[1] - 0.5*inch)
        
        # Contact info (right side, italics)
        canvas.setFont('Times-Italic', 10)
        right_x = letter[0] - inch
        top_y = letter[1] - 0.5*inch
        
        canvas.drawRightString(right_x, top_y, attorney.get('name', ''))
        canvas.drawRightString(right_x, top_y - 12, contact.get('address', ''))
        canvas.drawRightString(right_x, top_y - 24, 
            f"{contact.get('city', '')}, {contact.get('state', '')} {contact.get('zip', '')}")
        canvas.drawRightString(right_x, top_y - 36, f"Ph: {contact.get('phone', '')}")
        canvas.drawRightString(right_x, top_y - 48, f"Fax: {contact.get('fax', '')}")
        
        canvas.restoreState()
    
    def _draw_whaley_logo(self, canvas, x, y):
        """Draw the Whaley Law Firm logo matching the official letterhead."""
        # Draw the stylized W with horizontal lines
        canvas.saveState()
        
        # Draw horizontal lines through the W area (left side decoration)
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1)
        for i in range(5):
            line_y = y - 20 - (i * 8)
            canvas.line(x, line_y, x + 30, line_y)
        
        # Draw large "W" overlapping the lines
        canvas.setFont('Times-Bold', 48)
        canvas.drawString(x + 5, y - 55, "W")
        
        # Draw "THE" above HALEY
        canvas.setFont('Times-Roman', 8)
        canvas.drawString(x + 48, y - 12, "THE")
        
        # Draw "HALEY" in large bold
        canvas.setFont('Times-Bold', 32)
        canvas.drawString(x + 45, y - 45, "HALEY")
        
        # Draw horizontal line under WHALEY
        canvas.setLineWidth(0.5)
        canvas.line(x + 45, y - 52, x + 175, y - 52)
        
        # Draw "LAW  F I R M" spaced out below
        canvas.setFont('Times-Roman', 12)
        canvas.drawString(x + 70, y - 68, "L A W    F I R M")
        
        canvas.restoreState()
    
    def _later_page_header(self, canvas, doc):
        """Simple header for subsequent pages."""
        canvas.saveState()
        # Just page number at bottom
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(letter[0]/2, 0.5*inch, f"Page {doc.page}")
        canvas.restoreState()


def create_styles(config: Dict[str, Any]) -> Dict[str, ParagraphStyle]:
    """Create paragraph styles matching the demand letter format."""
    formatting = config.get('formatting', {})
    
    styles = {
        'date': ParagraphStyle(
            'date',
            fontName='Times-Roman',
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=24,
        ),
        'confidential': ParagraphStyle(
            'confidential',
            fontName='Times-Bold',
            fontSize=12,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        'recipient': ParagraphStyle(
            'recipient',
            fontName='Times-Roman',
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        're_line': ParagraphStyle(
            're_line',
            fontName='Times-Roman',
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            leftIndent=0.5*inch,
            spaceAfter=4,
        ),
        'salutation': ParagraphStyle(
            'salutation',
            fontName='Times-Roman',
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=12,
        ),
        'body': ParagraphStyle(
            'body',
            fontName='Times-Roman',
            fontSize=12,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            firstLineIndent=0,
        ),
        'section_header': ParagraphStyle(
            'section_header',
            fontName='Times-Bold',
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            spaceBefore=18,
            spaceAfter=12,
        ),
        'subsection_header': ParagraphStyle(
            'subsection_header',
            fontName='Times-Bold',
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=8,
        ),
        'provider_header': ParagraphStyle(
            'provider_header',
            fontName='Times-Bold',
            fontSize=12,
            leading=14,
            alignment=TA_CENTER,
            spaceBefore=12,
            spaceAfter=8,
            backColor=colors.HexColor('#E0E0E0'),
        ),
        'bullet': ParagraphStyle(
            'bullet',
            fontName='Times-Roman',
            fontSize=12,
            leading=14,
            alignment=TA_JUSTIFY,
            leftIndent=0.5*inch,
            bulletIndent=0.25*inch,
            spaceAfter=6,
        ),
        'signature': ParagraphStyle(
            'signature',
            fontName='Times-Roman',
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            spaceBefore=24,
        ),
        'exhibit_separator': ParagraphStyle(
            'exhibit_separator',
            fontName='Times-Bold',
            fontSize=48,
            leading=52,
            alignment=TA_CENTER,
        ),
    }
    
    return styles


def generate_demand_pdf(
    parsed_data: Dict[str, Any],
    output_path: str,
    config: Dict[str, Any]
) -> str:
    """
    Generate the demand letter PDF (without exhibits).
    Returns path to generated PDF.
    """
    styles = create_styles(config)
    metadata = parsed_data.get('metadata', {})
    sections = parsed_data.get('sections', {})
    tables = parsed_data.get('tables', {})
    photos = parsed_data.get('photos', [])
    exhibits = parsed_data.get('exhibits', [])
    
    # Build story (list of flowables)
    story = []
    
    # Date
    today = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(today, styles['date']))
    story.append(Spacer(1, 12))
    
    # Confidential header
    demand_config = config.get('demand_letter', {})
    conf_header = demand_config.get('confidential_header', 
        'CONFIDENTIAL AND INADMISSIBLE\nOFFER OF COMPROMISE PURSUANT TO KENTUCKY RULE OF EVIDENCE 408')
    for line in conf_header.split('\n'):
        story.append(Paragraph(f"<u>{line}</u>", styles['confidential']))
    story.append(Spacer(1, 12))
    
    # Recipient info
    adjuster_email = metadata.get('adjuster_email', '')
    if adjuster_email:
        story.append(Paragraph(f"<b>Email: {adjuster_email}</b>", styles['recipient']))
        story.append(Spacer(1, 12))
    
    # RE: block
    story.append(Paragraph(f"<b>Re:</b>", styles['recipient']))
    re_items = [
        ('Our Client:', metadata.get('client_name', '[Client Name]')),
        ('Defendant:', metadata.get('defendant_name', '[Defendant]')),
        ('Date of Incident:', metadata.get('date_of_incident', '[Date]')),
    ]
    if metadata.get('claim_number'):
        re_items.append(('Claim #:', metadata.get('claim_number')))
    
    for label, value in re_items:
        story.append(Paragraph(f"<b>{label}</b>&nbsp;&nbsp;&nbsp;{value}", styles['re_line']))
    story.append(Spacer(1, 18))
    
    # Salutation
    adjuster_name = metadata.get('adjuster_name', 'Claims Professional')
    insurance = metadata.get('insurance_company', 'Insurance Company')
    story.append(Paragraph(
        f"Dear {adjuster_name} and All {insurance} Decision-Makers:",
        styles['salutation']
    ))
    
    # Section numbering
    section_num = 1
    
    # INTRODUCTION section
    if 'INTRODUCTION' in sections:
        intro_content = sections['INTRODUCTION']
        # Parse paragraphs (split by double newline)
        paragraphs = re.split(r'\n\n+', intro_content)
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('#'):
                # Convert markdown bold/italic
                para = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para)
                para = re.sub(r'\*(.+?)\*', r'<i>\1</i>', para)
                story.append(Paragraph(para, styles['body']))
    
    # FACTS & LIABILITY section
    if 'FACTS & LIABILITY' in sections:
        story.append(Paragraph(f"<b>{section_num}. FACTS & LIABILITY</b>", styles['section_header']))
        section_num += 1
        
        facts_content = sections['FACTS & LIABILITY']
        
        # Check for Photos subsection
        if '## Photos' in facts_content:
            parts = facts_content.split('## Photos')
            facts_text = parts[0]
        else:
            facts_text = facts_content
        
        # Parse paragraphs and bullets
        for para in re.split(r'\n\n+', facts_text):
            para = para.strip()
            if not para or para.startswith('#'):
                continue
            
            # Handle bullet lists
            if para.startswith('-'):
                for bullet in para.split('\n'):
                    bullet = bullet.strip()
                    if bullet.startswith('-'):
                        bullet_text = bullet[1:].strip()
                        bullet_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', bullet_text)
                        story.append(Paragraph(f"• {bullet_text}", styles['bullet']))
            else:
                para = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para)
                para = re.sub(r'\*(.+?)\*', r'<i>\1</i>', para)
                story.append(Paragraph(para, styles['body']))
        
        # Embed photos if any
        for caption, photo_path in photos:
            if os.path.exists(photo_path):
                try:
                    img = Image(photo_path, width=3*inch, height=3*inch)
                    img.hAlign = 'CENTER'
                    story.append(Spacer(1, 12))
                    story.append(img)
                    story.append(Paragraph(f"<i>{caption}</i>", styles['body']))
                    story.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Warning: Could not embed photo {photo_path}: {e}")
    
    # INJURIES & TREATMENTS section
    if 'INJURIES & TREATMENTS' in sections:
        story.append(Paragraph(f"<b>{section_num}. INJURIES & TREATMENTS</b>", styles['section_header']))
        section_num += 1
        
        injuries_content = sections['INJURIES & TREATMENTS']
        
        # Summary of Injuries table
        story.append(Paragraph("<b>2.1. Summary of Injuries</b>", styles['subsection_header']))
        story.append(Paragraph(
            "We have enclosed all pertinent medical information regarding our client's injuries. "
            "These injuries were suffered as a direct and proximate result of this incident. "
            "The chart below represents a non-exhaustive summary of the injuries sustained by our client:",
            styles['body']
        ))
        
        # Get injuries table
        if 'INJURIES & TREATMENTS' in tables and tables['INJURIES & TREATMENTS']:
            injury_table = tables['INJURIES & TREATMENTS'][0]
            if injury_table:
                # Create ReportLab table with Paragraph objects for text wrapping
                # Define cell styles
                header_style = ParagraphStyle(
                    'TableHeader',
                    fontName='Times-Bold',
                    fontSize=11,
                    textColor=colors.white,
                    alignment=TA_LEFT,
                )
                cell_style = ParagraphStyle(
                    'TableCell',
                    fontName='Times-Roman',
                    fontSize=11,
                    alignment=TA_LEFT,
                    leading=13,
                )
                code_style = ParagraphStyle(
                    'TableCode',
                    fontName='Times-Roman',
                    fontSize=11,
                    alignment=TA_CENTER,
                    leading=13,
                )
                
                # Build table data with Paragraph objects
                table_data = []
                # Header row
                header_row = [
                    Paragraph(injury_table[0][0], header_style),
                    Paragraph(injury_table[0][1] if len(injury_table[0]) > 1 else '', header_style),
                ]
                table_data.append(header_row)
                
                # Data rows
                for row in injury_table[1:]:
                    data_row = [
                        Paragraph(row[0] if len(row) > 0 else '', cell_style),
                        Paragraph(row[1] if len(row) > 1 else '', code_style),
                    ]
                    table_data.append(data_row)
                
                t = Table(table_data, colWidths=[4.5*inch, 1.5*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#404040')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(t)
                story.append(Spacer(1, 18))
        
        # Treatment Chronology
        story.append(Paragraph("<b>2.2. Treatment</b>", styles['subsection_header']))
        
        # Parse provider blocks
        providers = parse_provider_blocks(injuries_content)
        for provider in providers:
            # Provider header (gray bar)
            story.append(Spacer(1, 6))
            provider_table = Table(
                [[provider['name']]],
                colWidths=[6*inch]
            )
            provider_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E0E0E0')),
                ('FONTNAME', (0, 0), (-1, -1), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(provider_table)
            
            # Provider details
            if provider['timeline']:
                story.append(Paragraph(
                    f"<b>Treatment Timeline</b>&nbsp;&nbsp;&nbsp;{provider['timeline']}",
                    styles['body']
                ))
            if provider['visits']:
                story.append(Paragraph(
                    f"<b>Number of Visits</b>&nbsp;&nbsp;&nbsp;{provider['visits']}",
                    styles['body']
                ))
            if provider['summary']:
                story.append(Paragraph("<b>Summary</b>", styles['body']))
                for bullet in provider['summary']:
                    bullet = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', bullet)
                    story.append(Paragraph(f"• {bullet}", styles['bullet']))
            if provider['exhibit']:
                story.append(Paragraph(
                    f"<b>Supporting Documents</b>&nbsp;&nbsp;&nbsp;{provider['exhibit']}",
                    styles['body']
                ))
    
    # SPECIAL DAMAGES section
    if 'SPECIAL DAMAGES' in sections:
        story.append(Paragraph(f"<b>{section_num}. SPECIAL DAMAGES</b>", styles['section_header']))
        section_num += 1
        
        damages_content = sections['SPECIAL DAMAGES']
        subsections = re.split(r'^##\s+', damages_content, flags=re.MULTILINE)
        
        sub_num = 1
        for subsection in subsections[1:]:  # Skip content before first ##
            lines = subsection.strip().split('\n')
            if not lines:
                continue
            
            subsection_name = lines[0].strip()
            subsection_content = '\n'.join(lines[1:])
            
            story.append(Paragraph(
                f"<b>3.{sub_num}. {subsection_name}</b>",
                styles['subsection_header']
            ))
            sub_num += 1
            
            # Check for tables in this subsection
            subsection_tables = parse_markdown_tables(subsection_content)
            
            # Add text content (non-table)
            text_content = re.sub(r'\|.*\|', '', subsection_content)
            for para in re.split(r'\n\n+', text_content):
                para = para.strip()
                if para and not para.startswith('|'):
                    para = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para)
                    story.append(Paragraph(para, styles['body']))
            
            # Add tables with Paragraph objects for text wrapping
            for raw_table_data in subsection_tables:
                if raw_table_data:
                    # Define cell styles
                    header_style = ParagraphStyle(
                        'DamagesHeader',
                        fontName='Times-Bold',
                        fontSize=11,
                        textColor=colors.white,
                        alignment=TA_LEFT,
                    )
                    cell_style = ParagraphStyle(
                        'DamagesCell',
                        fontName='Times-Roman',
                        fontSize=11,
                        alignment=TA_LEFT,
                        leading=13,
                    )
                    amount_style = ParagraphStyle(
                        'DamagesAmount',
                        fontName='Times-Roman',
                        fontSize=11,
                        alignment=TA_RIGHT,
                        leading=13,
                    )
                    
                    # Build wrapped table
                    wrapped_table_data = []
                    for i, row in enumerate(raw_table_data):
                        if i == 0:  # Header
                            wrapped_row = [Paragraph(cell, header_style) for cell in row]
                        else:  # Data rows
                            wrapped_row = []
                            for j, cell in enumerate(row):
                                if j == len(row) - 1:  # Last column (amount)
                                    wrapped_row.append(Paragraph(cell, amount_style))
                                else:
                                    wrapped_row.append(Paragraph(cell, cell_style))
                        wrapped_table_data.append(wrapped_row)
                    
                    # Determine column widths based on number of columns
                    num_cols = len(raw_table_data[0]) if raw_table_data else 3
                    if num_cols == 3:
                        col_widths = [2.5*inch, 2*inch, 1.5*inch]
                    elif num_cols == 2:
                        col_widths = [4*inch, 2*inch]
                    else:
                        col_widths = [6*inch / num_cols] * num_cols
                    
                    t = Table(wrapped_table_data, colWidths=col_widths)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#404040')),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 12))
    
    # DEMAND section
    if 'DEMAND' in sections:
        story.append(Paragraph(f"<b>{section_num}. DEMAND TO SETTLE</b>", styles['section_header']))
        section_num += 1
        
        demand_content = sections['DEMAND']
        for para in re.split(r'\n\n+', demand_content):
            para = para.strip()
            if para and not para.startswith('#'):
                para = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para)
                story.append(Paragraph(para, styles['body']))
    
    # Signature
    story.append(Spacer(1, 24))
    story.append(Paragraph("Sincerely,", styles['signature']))
    story.append(Spacer(1, 36))
    
    attorney = config.get('attorney', {})
    story.append(Paragraph(f"<u><b>{attorney.get('name', '')}</b></u>", styles['signature']))
    story.append(Paragraph(attorney.get('name', ''), styles['signature']))
    
    # Exhibit list
    if exhibits:
        story.append(PageBreak())
        story.append(Paragraph("<u><b>Exhibit List</b></u>", styles['section_header']))
        story.append(Spacer(1, 12))
        
        exhibit_data = [['Exhibit No.', 'Description']]
        for i, (desc, path) in enumerate(exhibits, 1):
            exhibit_data.append([str(i), desc])
        
        t = Table(exhibit_data, colWidths=[1*inch, 5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#404040')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
    
    # Build PDF
    doc = DemandDocTemplate(
        output_path,
        config,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=1.5*inch,
        bottomMargin=inch
    )
    
    # Use first page template, then switch to later pages
    story.insert(0, NextPageTemplate('Later'))
    
    doc.build(story)
    return output_path


# =============================================================================
# Exhibit Compilation
# =============================================================================

def create_exhibit_separator(exhibit_num: int, description: str, output_path: str, config: Dict[str, Any]):
    """Create a single exhibit separator page."""
    from reportlab.pdfgen import canvas as pdf_canvas
    
    c = pdf_canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Large centered exhibit number
    c.setFont('Times-Bold', 48)
    c.drawCentredString(width/2, height/2 + 30, f"EXHIBIT {exhibit_num}")
    
    # Description below
    c.setFont('Times-Roman', 14)
    c.drawCentredString(width/2, height/2 - 30, description)
    
    c.save()
    return output_path


def compile_exhibits(
    exhibits: List[Tuple[str, str]],
    demand_pdf_path: str,
    output_path: str,
    config: Dict[str, Any]
) -> str:
    """
    Compile the demand letter with all exhibits.
    
    For each exhibit:
    1. Add a separator page (EXHIBIT 1, EXHIBIT 2, etc.)
    2. Append the actual exhibit PDF
    
    Returns path to final combined PDF.
    """
    import tempfile
    
    writer = PdfWriter()
    
    # Add demand letter
    demand_reader = PdfReader(demand_pdf_path)
    for page in demand_reader.pages:
        writer.add_page(page)
    
    # Add exhibits
    for i, (description, exhibit_path) in enumerate(exhibits, 1):
        # Create separator page
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            separator_path = tmp.name
        
        create_exhibit_separator(i, description, separator_path, config)
        
        # Add separator
        separator_reader = PdfReader(separator_path)
        for page in separator_reader.pages:
            writer.add_page(page)
        
        # Clean up temp file
        os.unlink(separator_path)
        
        # Add exhibit PDF
        if os.path.exists(exhibit_path):
            try:
                exhibit_reader = PdfReader(exhibit_path)
                for page in exhibit_reader.pages:
                    writer.add_page(page)
            except Exception as e:
                print(f"Warning: Could not add exhibit {exhibit_path}: {e}")
        else:
            print(f"Warning: Exhibit file not found: {exhibit_path}")
    
    # Write combined PDF
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    return output_path


# =============================================================================
# Main Entry Point
# =============================================================================

def create_full_demand_packet(
    md_path: str,
    output_path: str,
    config_path: Optional[str] = None
) -> str:
    """
    Main function to create complete demand packet.
    
    Args:
        md_path: Path to filled markdown template
        output_path: Path for output PDF
        config_path: Optional path to firm config JSON
    
    Returns:
        Path to generated PDF
    """
    # Load config
    config = load_firm_config(config_path)
    
    # Parse markdown
    print(f"Parsing markdown template: {md_path}")
    parsed = parse_demand_markdown(md_path)
    
    print(f"Found {len(parsed['sections'])} sections")
    print(f"Found {len(parsed['photos'])} photos")
    print(f"Found {len(parsed['exhibits'])} exhibits")
    
    # Generate demand letter PDF (without exhibits)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        demand_only_path = tmp.name
    
    print("Generating demand letter PDF...")
    generate_demand_pdf(parsed, demand_only_path, config)
    
    # If no exhibits, just rename
    if not parsed['exhibits']:
        os.rename(demand_only_path, output_path)
        print(f"Demand letter saved to: {output_path}")
        return output_path
    
    # Compile with exhibits
    print("Compiling exhibits...")
    compile_exhibits(parsed['exhibits'], demand_only_path, output_path, config)
    
    # Clean up
    os.unlink(demand_only_path)
    
    print(f"Complete demand packet saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate demand letter PDF from markdown template'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to filled markdown demand template'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Path for output PDF'
    )
    parser.add_argument(
        '--config', '-c',
        help='Path to firm config JSON (defaults to firm_config.json in same directory)'
    )
    
    args = parser.parse_args()
    
    try:
        create_full_demand_packet(args.input, args.output, args.config)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

