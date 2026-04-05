from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from datetime import datetime
import os

def generate_report(violations):
    """Generate PDF report"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = f"violations_report_{timestamp}.pdf"
    
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=1
    )
    
    content = []
    
    # Title
    content.append(Paragraph("VWatch Traffic Violation Report", title_style))
    content.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                            styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Summary
    content.append(Paragraph(f"Total Violations: {len(violations)}", styles['Heading2']))
    content.append(Spacer(1, 30))
    
    # Each violation
    for i, v in enumerate(violations, 1):
        content.append(Paragraph(f"Violation #{i}", styles['Heading3']))
        content.append(Spacer(1, 10))
        
        content.append(Paragraph(f"<b>License Plate:</b> {v['plate']}", styles['Normal']))
        content.append(Paragraph(f"<b>Time:</b> {v['timestamp']}", styles['Normal']))
        content.append(Spacer(1, 10))
        
        if os.path.exists(v['image']):
            content.append(Image(v['image'], width=4*inch, height=3*inch))
        
        content.append(Spacer(1, 30))
    
    doc.build(content)
    return file_path