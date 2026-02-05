
def manage_bonafide(request):
    """View for HOD to manage bonafide requests."""
    if 'staff_id' not in request.session:
        return redirect('staffs:stafflogin')
    
    try:
        staff = Staff.objects.get(staff_id=request.session['staff_id'])
        if staff.role != 'HOD':
            messages.error(request, "Access Denied: Only HOD can manage bonafide requests.")
            return redirect('staffs:staff_dashboard')
    except Staff.DoesNotExist:
         return redirect('staffs:stafflogin')

    from students.models import BonafideRequest

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action') # 'approve' or 'reject'
        rejection_reason = request.POST.get('rejection_reason', '')

        if request_id and action:
            bonafide_req = get_object_or_404(BonafideRequest, id=request_id)
            
            if action == 'approve':
                bonafide_req.status = 'Approved'
                bonafide_req.save()
                messages.success(request, f"Bonafide request for {bonafide_req.student.student_name} approved.")
            elif action == 'reject':
                bonafide_req.status = 'Rejected'
                bonafide_req.rejection_reason = rejection_reason
                bonafide_req.save()
                messages.warning(request, f"Bonafide request for {bonafide_req.student.student_name} rejected.")
                
            return redirect('staffs:manage_bonafide')

    # Fetch all requests, ordered by pending first, then date
    requests = BonafideRequest.objects.all().order_by(
        Case(When(status='Pending HOD', then=0), default=1),
        '-created_at'
    )

    return render(request, 'staff/manage_bonafide.html', {
        'requests': requests,
        'staff': staff
    })
