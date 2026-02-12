import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

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


def send_parent_notification_email(student, remark_types, staff_name):
    """
    Send email notification to parent about student discipline remarks.
    
    Args:
        student: Student object
        remark_types: List of remark type display names
        staff_name: Name of staff who recorded the remarks
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    import logging
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.core.mail import EmailMultiAlternatives

    logger = logging.getLogger(__name__)

    try:
        # Get parent email from student's personal info
        parent_email = None
        if hasattr(student, 'personalinfo') and student.personalinfo:
            parent_email = student.personalinfo.parent_email
        
        if not parent_email:
            logger.warning(f"No parent email found for student {student.roll_number}")
            return False
        
        # Prepare email content
        subject = f"Student Discipline Notification - {student.student_name}"
        
        # Context for the template
        context = {
            'student_name': student.student_name,
            'roll_number': student.roll_number,
            'program': student.program_level,
            'semester': student.current_semester,
            'remark_types': remark_types,
            'date': timezone.now().strftime('%d-%m-%Y'),
            'staff_name': staff_name,
        }

        # Render HTML content
        html_content = render_to_string('emails/student_remark_notification.html', context)
        # Create plain text alternative
        text_content = strip_tags(html_content)
        
        # Create Email object
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[parent_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send
        email.send(fail_silently=False)
        
        logger.info(f"Email sent successfully to {parent_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def send_attendance_deficit_email(student, month_name, percentage, total_hours, attended_hours, staff_name):
    """
    Send low attendance alert email.
    """
    import logging
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.core.mail import EmailMultiAlternatives

    logger = logging.getLogger(__name__)

    try:
        parent_email = None
        if hasattr(student, 'personalinfo') and student.personalinfo:
            parent_email = student.personalinfo.parent_email
        
        if not parent_email:
            return False

        subject = f"Low Attendance Alert - {student.student_name} - {month_name}"
        
        context = {
            'student_name': student.student_name,
            'roll_number': student.roll_number,
            'program': student.program_level,
            'semester': student.current_semester,
            'month_name': month_name,
            'percentage': percentage,
            'total_hours': total_hours,
            'attended_hours': attended_hours,
            'staff_name': staff_name,
        }

        html_content = render_to_string('emails/attendance_deficit_notification.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[parent_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True

    except Exception as e:
        logger.error(f"Error sending attendance email: {e}")
        return False
