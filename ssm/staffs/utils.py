import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.conf import settings
from django.utils import timezone

def draw_bonafide_content(p, request):
    """
    Helper function to draw the content of a single bonafide certificate on a canvas.
    """
    width, height = A4
    
    # --- BORDERS ---
    # Outer Border (Thick)
    p.setStrokeColor(colors.darkblue)
    p.setLineWidth(3)
    p.rect(0.4*inch, 0.4*inch, width-0.8*inch, height-0.8*inch)
    
    # Inner Border (Thin, Gold/Orange accent if color allowed, otherwise black)
    p.setStrokeColor(colors.black) 
    p.setLineWidth(1)
    p.rect(0.6*inch, 0.6*inch, width-1.2*inch, height-1.2*inch)
    
    # --- HEADER ---
    # Logo Placeholder (Text for now)
    p.setFont("Helvetica-Bold", 10)
    # p.drawImage("path/to/logo.png", 1*inch, height - 1.5*inch, width=1*inch, height=1*inch) # If logo existed
    
    p.setFillColor(colors.darkblue)
    p.setFont("Helvetica-Bold", 26)
    p.drawCentredString(width/2, height - 1.8*inch, "ANNAMALAI UNIVERSITY")
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, height - 2.1*inch, "(Accredited with 'A' Grade by NAAC)")
    
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height - 3*inch, "BONAFIDE CERTIFICATE")
    
    # --- DATE ---
    p.setFont("Helvetica", 11)
    date_str = timezone.now().strftime("%d-%m-%Y")
    p.drawRightString(width - 1.5*inch, height - 3.8*inch, f"Date: {date_str}")
    
    # --- CONTENT BODY ---
    p.setFont("Times-Roman", 14) # Serif font looks more official
    text_y = height - 5*inch
    line_height = 30 # More spacing
    
    # Justified-like text simulation
    p.drawCentredString(width/2, text_y, "This is to certify that")
    text_y -= line_height
    
    p.setFont("Times-Bold", 16)
    p.drawCentredString(width/2, text_y, f"Mr./Ms. {request.student.student_name.upper()}")
    text_y -= line_height
    
    p.setFont("Times-Roman", 14)
    p.drawCentredString(width/2, text_y, f"(Roll Number: {request.student.roll_number})")
    text_y -= line_height * 1.5
    
    p.drawCentredString(width/2, text_y, f"is a bonafide student of Semester {request.student.current_semester}")
    text_y -= line_height
    
    p.drawCentredString(width/2, text_y, "in the Department of Information Technology")
    text_y -= line_height
    
    p.drawCentredString(width/2, text_y, "during the academic year 2025-2026.")
    text_y -= line_height * 2
    
    # --- PURPOSE ---
    # p.setFont("Times-Bold", 12)
    # p.drawString(1.5*inch, text_y, "Purpose:")
    # p.setFont("Times-Roman", 12)
    # p.drawString(2.3*inch, text_y, request.reason)
    
    # --- FOOTER / SIGNATURES ---
    bottom_margin = 2*inch
    
    # Seal Box
    p.setLineWidth(1)
    p.rect(1.5*inch, bottom_margin, 1.5*inch, 1.5*inch)
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(2.25*inch, bottom_margin + 0.75*inch, "Department Seal")
    
    # HOD Signature
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - 1.5*inch, bottom_margin + 0.5*inch, "Head of Department")
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 1.5*inch, bottom_margin + 0.2*inch, "(Signature & Seal)")

def generate_bonafide_pdf(buffer, request_obj):
    """
    Generates a single Bonafide Certificate PDF.
    """
    p = canvas.Canvas(buffer, pagesize=A4)
    draw_bonafide_content(p, request_obj)
    p.showPage()
    p.save()

def generate_bulk_bonafide_pdf(buffer, request_objs):
    """
    Generates a PDF containing multiple Bonafide Certificates (one per page).
    """
    p = canvas.Canvas(buffer, pagesize=A4)
    for req in request_objs:
        draw_bonafide_content(p, req)
        p.showPage() # New page for next certificate
    p.save()

def log_audit(request, action, actor_type, actor_id, actor_name=None, object_type=None, object_id=None, message=None):
    """
    Logs an audit trail entry.
    """
    from .models import AuditLog

    # Get Client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    # Get User Agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    AuditLog.objects.create(
        action=action,
        actor_type=actor_type,
        actor_id=actor_id or '',
        actor_name=actor_name or '',
        object_type=object_type or '',
        object_id=object_id or '',
        ip_address=ip_address,
        user_agent=user_agent,
        message=message or '',
        timestamp=timezone.now()
    )
