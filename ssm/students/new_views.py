
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

@student_login_required
def bonafide_list(request):
    """Lists student's bonafide requests."""
    roll_number = request.session.get('student_roll_number')
    student = Student.objects.get(roll_number=roll_number)
    
    requests = BonafideRequest.objects.filter(student=student).order_by('-created_at')
    
    # Handle New Request Submission (if done from this page)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        if not reason:
             messages.error(request, 'Reason is required.')
        else:
            # Check limit: 1 per month
            now = timezone.now()
            start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            existing_count = BonafideRequest.objects.filter(
                student=student,
                created_at__gte=start_month
            ).count()
            
            limit = 2
            if existing_count >= limit:
                 messages.error(request, f'You have already requested a Bonafide Certificate {limit} times this month. Limit reached.')
            else:
                BonafideRequest.objects.create(student=student, reason=reason)
                messages.success(request, 'Bonafide Request submitted successfully to HOD!')
                return redirect('bonafide_list')

    return render(request, 'bonafide_list.html', {'requests': requests, 'student': student})

@student_login_required
def download_bonafide(request, request_id):
    """Generates PDF for approved bona fide certificate."""
    roll_number = request.session.get('student_roll_number')
    student = Student.objects.get(roll_number=roll_number)
    
    bonafide = get_object_or_404(BonafideRequest, id=request_id, student=student)
    
    if bonafide.status != 'Approved':
        messages.error(request, 'Certificate is not approved yet.')
        return redirect('bonafide_list')
        
    template_path = 'bonafide_certificate_pdf.html'
    context = {
        'bonafide': bonafide,
        'student': student,
        'date': timezone.now()
    }
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"Bonafide_{student.roll_number}_{bonafide.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
