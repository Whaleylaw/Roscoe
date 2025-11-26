"""
Quality Metrics & PDF Classification

Assesses extraction quality and classifies PDFs to determine optimal processing method.
"""

from pathlib import Path


def classify_pdf(pdf_path, sample_pages=3):
    """
    Classify PDF as text-based or scanned by attempting text extraction.

    Args:
        pdf_path: Path to PDF file
        sample_pages: Number of pages to sample (default: 3)

    Returns:
        dict: {
            'classification': 'text_based' | 'scanned' | 'mixed',
            'confidence': 'high' | 'medium' | 'low',
            'recommendation': 'pdfplumber' | 'ocr' | 'hybrid',
            'details': dict
        }
    """
    try:
        import pdfplumber
    except ImportError:
        return {
            'classification': 'unknown',
            'confidence': 'low',
            'recommendation': 'ocr',
            'error': 'pdfplumber not installed - cannot classify PDF'
        }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            pages_to_check = min(sample_pages, num_pages)

            # Sample first, middle, and last pages
            if num_pages == 1:
                sample_indices = [0]
            elif num_pages == 2:
                sample_indices = [0, 1]
            else:
                sample_indices = [
                    0,  # First page
                    num_pages // 2,  # Middle page
                    num_pages - 1  # Last page
                ][:pages_to_check]

            total_chars = 0
            page_char_counts = []

            for idx in sample_indices:
                page_text = pdf.pages[idx].extract_text()
                char_count = len(page_text.strip()) if page_text else 0
                page_char_counts.append(char_count)
                total_chars += char_count

            avg_chars = total_chars / len(sample_indices) if sample_indices else 0

            # Classification logic
            if avg_chars > 500:
                # High text content - likely text-based PDF
                classification = 'text_based'
                confidence = 'high'
                recommendation = 'pdfplumber'
            elif avg_chars > 100:
                # Medium text content - could be mixed or poor-quality text PDF
                classification = 'mixed'
                confidence = 'medium'
                recommendation = 'hybrid'  # Try pdfplumber, fall back to OCR
            else:
                # Low/no text content - likely scanned
                classification = 'scanned'
                confidence = 'high'
                recommendation = 'ocr'

            # Check for consistency across pages
            if page_char_counts:
                variance = max(page_char_counts) - min(page_char_counts)
                if variance > 1000:
                    # High variance suggests mixed document
                    classification = 'mixed'
                    confidence = 'medium'

            return {
                'classification': classification,
                'confidence': confidence,
                'recommendation': recommendation,
                'details': {
                    'total_pages': num_pages,
                    'pages_sampled': len(sample_indices),
                    'avg_chars_per_page': avg_chars,
                    'page_char_counts': page_char_counts,
                    'total_sample_chars': total_chars
                }
            }

    except Exception as e:
        return {
            'classification': 'unknown',
            'confidence': 'low',
            'recommendation': 'ocr',
            'error': f'Classification failed: {str(e)}'
        }


def assess_quality(result):
    """
    Assess extraction quality from a processor result.

    Args:
        result: Result dict from extract_with_pdfplumber() or extract_with_ocr()

    Returns:
        dict: {
            'overall_quality': 'excellent' | 'good' | 'fair' | 'poor',
            'needs_cloud_ai': bool,
            'confidence_score': float (0-100),
            'issues': list,
            'metrics': dict
        }
    """
    if not result.get('success'):
        return {
            'overall_quality': 'failed',
            'needs_cloud_ai': True,
            'confidence_score': 0,
            'issues': [result.get('error', 'Unknown error')],
            'metrics': {}
        }

    method = result.get('method', 'unknown')
    char_count = result.get('char_count', 0)
    page_count = result.get('page_count', 0)

    avg_chars_per_page = char_count / page_count if page_count > 0 else 0

    issues = []
    confidence_score = 100

    # Assess based on method
    if method == 'pdfplumber':
        # PDFPlumber results are generally high quality
        if avg_chars_per_page < 100:
            issues.append('Low text density - document may be scanned')
            confidence_score -= 50
        elif avg_chars_per_page < 300:
            issues.append('Medium text density - document may have images/tables')
            confidence_score -= 20

    elif method == 'ocr':
        # OCR results have inherent uncertainty
        ocr_confidence = result.get('confidence', 'medium')

        if ocr_confidence == 'low':
            issues.append('Low OCR confidence - poor scan quality')
            confidence_score -= 60
        elif ocr_confidence == 'medium':
            issues.append('Medium OCR confidence - scan quality acceptable')
            confidence_score -= 30
        else:
            confidence_score -= 10  # Even good OCR has some uncertainty

    # Check for extremely low output
    if char_count < 50:
        issues.append('Very low character count - extraction may have failed')
        confidence_score -= 40

    # Determine overall quality
    if confidence_score >= 80:
        overall_quality = 'excellent'
        needs_cloud_ai = False
    elif confidence_score >= 60:
        overall_quality = 'good'
        needs_cloud_ai = False
    elif confidence_score >= 40:
        overall_quality = 'fair'
        needs_cloud_ai = True  # Consider cloud processing
    else:
        overall_quality = 'poor'
        needs_cloud_ai = True

    return {
        'overall_quality': overall_quality,
        'needs_cloud_ai': needs_cloud_ai,
        'confidence_score': max(0, confidence_score),
        'issues': issues,
        'metrics': {
            'method': method,
            'char_count': char_count,
            'page_count': page_count,
            'avg_chars_per_page': avg_chars_per_page,
            'table_count': result.get('table_count', 0)
        }
    }
