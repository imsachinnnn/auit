from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from .models import Staff
from students.models import BonafideRequest
from .utils import generate_bonafide_pdf, generate_bulk_bonafide_pdf
import io

@login_required(login_url='staffs:stafflogin')
def generate_bonafide_request_pdf(request, request_id):
    """Generates PDF for a specific bonafide request."""
    bonafide_req = get_object_or_404(BonafideRequest, id=request_id)
    buffer = io.BytesIO()
    generate_bonafide_pdf(buffer, bonafide_req)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=f"bonafide_{bonafide_req.student.roll_number}.pdf")

@login_required(login_url='staffs:stafflogin')
def hod_bonafide_list(request):
    """
    HOD View: Lists pending requests. actions: Approve / Reject.
    Strict role checks are initially disabled to ensure access.
    """
    print("DEBUG: Entered hod_bonafide_list")
    if 'staff_id' not in request.session:
        print("DEBUG: No staff_id in session, redirecting to login")
        return redirect('staffs:stafflogin')

    try:
        staff = Staff.objects.get(staff_id=request.session['staff_id'])
        print(f"DEBUG: Staff found: {staff.name} ({staff.role})")
    except Staff.DoesNotExist:
        print("DEBUG: Staff.DoesNotExist")
        return redirect('staffs:stafflogin')

    # POST: Handle Actions
    if request.method == 'POST':
        action = request.POST.get('action')
        req_id = request.POST.get('request_id')
        rejection_reason = request.POST.get('rejection_reason', '')

        bonafide_req = get_object_or_404(BonafideRequest, id=req_id)

        if action == 'approve':
            if bonafide_req.status == 'Pending HOD Approval':
                bonafide_req.status = 'Approved by HOD'
                bonafide_req.save()
                messages.success(request, f"Approved request for {bonafide_req.student.student_name}.")
        
        elif action == 'reject':
            bonafide_req.status = 'Rejected'
            bonafide_req.rejection_reason = rejection_reason
            bonafide_req.save()
            messages.warning(request, f"Rejected request for {bonafide_req.student.student_name}.")

        elif action == 'mark_collected':
             bonafide_req.status = 'Collected'
             bonafide_req.save()
             messages.success(request, "Marked as Collected.")

        return redirect('staffs:hod_manage_bonafide')

    # GET: List Data
    pending_requests = BonafideRequest.objects.filter(status='Pending HOD Approval').order_by('-created_at')
    # Approved requests now visible to HOD for printing/issuing
    approved_requests = BonafideRequest.objects.filter(status='Approved by HOD').order_by('-updated_at')
    history_requests = BonafideRequest.objects.exclude(status__in=['Pending HOD Approval', 'Approved by HOD']).order_by('-updated_at')[:20]

    context = {
        'staff': staff,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'history_requests': history_requests,
    }
    return render(request, 'staff/bonafide/hod_list.html', context)


@login_required(login_url='staffs:stafflogin')
def office_bonafide_list(request):
    """
    Office View: Lists requests with new workflow:
    Pending -> Waiting for HOD Sign -> Signed -> Collected
    """
    if 'staff_id' not in request.session:
        return redirect('staffs:stafflogin')

    try:
        staff = Staff.objects.get(staff_id=request.session['staff_id'])
    except Staff.DoesNotExist:
        return redirect('staffs:stafflogin')

    # POST: Handle Actions
    if request.method == 'POST':
        action = request.POST.get('action')
        req_id = request.POST.get('request_id')
        rejection_reason = request.POST.get('rejection_reason', '')
        
        # Handle Bulk Print
        if action == 'bulk_print':
             waiting_requests = BonafideRequest.objects.filter(status='Waiting for HOD Sign')
             if waiting_requests.exists():
                 buffer = io.BytesIO()
                 generate_bulk_bonafide_pdf(buffer, waiting_requests)
                 buffer.seek(0)
                 return FileResponse(buffer, as_attachment=False, filename="bonafide_batch_print.pdf")
             else:
                 messages.warning(request, "No requests waiting for signature.")
                 return redirect('staffs:office_manage_bonafide')

        # Request-specific actions
        bonafide_req = get_object_or_404(BonafideRequest, id=req_id)

        if action == 'approve':
             # PENDING -> WAITING FOR HOD SIGN
             bonafide_req.status = 'Waiting for HOD Sign'
             bonafide_req.save()
             messages.success(request, f"Approved request for {bonafide_req.student.student_name}. Moved to Waiting List.")

        elif action == 'reject':
            bonafide_req.status = 'Rejected'
            bonafide_req.rejection_reason = rejection_reason
            bonafide_req.save()
            messages.warning(request, f"Rejected request for {bonafide_req.student.student_name}.")

        elif action == 'mark_signed':
            # WAITING -> SIGNED (Ready for Collection)
            bonafide_req.status = 'Signed'
            bonafide_req.save()
            messages.success(request, "Marked as Signed & Ready for Collection.")
        
        elif action == 'mark_collected':
             # SIGNED -> COLLECTED
             bonafide_req.status = 'Collected'
             bonafide_req.save()
             messages.success(request, "Marked as Collected.")

        return redirect('staffs:office_manage_bonafide')

    # GET: List Data
    
    # 1. Pending Approval
    pending_requests = BonafideRequest.objects.filter(status='Pending Office Approval').order_by('created_at')
    
    # 2. Waiting for HOD Sign (Approved by Office, waiting for print/sign)
    # Include 'Approved by HOD' for legacy/transition support if any exists
    waiting_requests = BonafideRequest.objects.filter(status__in=['Waiting for HOD Sign', 'Approved by HOD']).order_by('updated_at')
    
    # 3. Ready for Collection (Signed)
    # Include 'Ready for Collection' for legacy/transition support
    ready_requests = BonafideRequest.objects.filter(status__in=['Signed', 'Ready for Collection']).order_by('updated_at')
    
    # 4. History
    processed_requests = BonafideRequest.objects.filter(status__in=['Collected', 'Rejected']).order_by('-updated_at')[:20]

    context = {
        'staff': staff,
        'pending_requests': pending_requests,
        'waiting_requests': waiting_requests,
        'ready_requests': ready_requests,
        'processed_requests': processed_requests,
    }
    return render(request, 'staff/bonafide/office_list.html', context)
