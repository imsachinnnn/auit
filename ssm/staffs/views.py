from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Staff
from students.models import Student
from django.db.models import Q

def stafflogin(request):
    """Handles staff login."""
    if 'staff_id' in request.session:
        return redirect('staffs:staff_dashboard')

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        password = request.POST.get('password')
        try:
            staff = Staff.objects.get(staff_id=staff_id)
            if staff.check_password(password):
                request.session['staff_id'] = staff.staff_id
                # --- THIS IS THE FIX ---
                # Use the correct URL name 'staff_dashboard' with the namespace
                return redirect('staffs:staff_dashboard')
            else:
                messages.error(request, 'Invalid Staff ID or Password.')
        except Staff.DoesNotExist:
            messages.error(request, 'Invalid Staff ID or Password.')
            
    return render(request, 'staff/stafflogin.html')


def staff_dashboard(request):
    """Displays the staff dashboard. Requires login."""
    if 'staff_id' not in request.session:
        return redirect('staffs:stafflogin')
    
    try:
        staff = Staff.objects.get(staff_id=request.session['staff_id'])
    except Staff.DoesNotExist:
        if 'staff_id' in request.session:
            del request.session['staff_id']
        return redirect('staffs:stafflogin')

    student_count = Student.objects.count()
    
    
    if staff.role == 'Class Incharge':
        template_name = 'staff/staffdash_class.html'
        # Filter students relevant to this class incharge
        if staff.assigned_semester:
            student_count = Student.objects.filter(current_semester=staff.assigned_semester).count()
        else:
            student_count = 0 # Or handle as "No semester assigned"
            
    elif staff.role == 'Course Incharge':
        template_name = 'staff/staffdash_course.html'
    else:
        template_name = 'staff/staffdash_hod.html' # Default HOD
        
    return render(request, template_name, {'staff': staff, 'student_count': student_count})


def staff_logout(request):
    """Logs the staff member out."""
    try:
        del request.session['staff_id']
    except KeyError:
        pass
    messages.success(request, "You have been successfully logged out.")
    return redirect('staffs:stafflogin')

def staff_register(request):
    """Handles the creation of a new staff member."""
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        
        if Staff.objects.filter(staff_id=staff_id).exists():
            messages.error(request, f"A staff member with the ID '{staff_id}' already exists.")
            return render(request, 'staff/staffreg.html')
        
        new_staff = Staff(
            staff_id=staff_id,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            photo=request.FILES.get('photo'),
            salutation=request.POST.get('salutation'),
            designation=request.POST.get('designation'),
            department=request.POST.get('department'),
            qualification=request.POST.get('qualification'),
            specialization=request.POST.get('specialization'),
            # role=request.POST.get('role'), REMOVED: Role is assigned by Admin, defaults to HOD in model
            date_of_birth=request.POST.get('date_of_birth') or None,
            date_of_joining=request.POST.get('date_of_joining') or None,
            address=request.POST.get('address'),
            academic_details=request.POST.get('academic_details'),
            experience=request.POST.get('experience'),
            publications=request.POST.get('publications'),
            awards_and_memberships=request.POST.get('awards_and_memberships'),
        )
        
        new_staff.set_password(request.POST.get('password'))
        new_staff.save()
        
        messages.success(request, f"Staff member {new_staff.name} has been registered successfully.")
        return redirect('staffs:stafflogin')

    return render(request, 'staff/staffreg.html')


def student_list(request):
    """Displays a list of students with search functionality for staff."""
    if 'staff_id' not in request.session:
        return redirect('staffs:stafflogin')

    query = request.GET.get('q')
    semester = request.GET.get('semester')
    
    
    students = Student.objects.all().select_related('studentdocuments')

    # Restrict view for Class Incharge
    try:
        current_staff = Staff.objects.get(staff_id=request.session['staff_id'])
        if current_staff.role == 'Class Incharge' and current_staff.assigned_semester:
            students = students.filter(current_semester=current_staff.assigned_semester)
            # Override semester filter to be the assigned one (or hide the filter in template)
            semester = str(current_staff.assigned_semester) 
    except Staff.DoesNotExist:
        pass

    if query:
        students = students.filter(
            Q(student_name__icontains=query) | 
            Q(roll_number__icontains=query) |
            Q(student_email__icontains=query)
        )
    
    if semester:
        try:
            semester_num = int(semester)
            if semester_num >= 9:
                students = students.filter(current_semester__gte=9)
            else:
                students = students.filter(current_semester=semester_num)
        except ValueError:
            pass  # ignore invalid semester input

    return render(request, 'studlist.html', {
        'students': students,
        'query': query,
        'selected_semester': semester
    })


def student_detail(request, roll_number):
    """Displays complete details of a single student."""
    if 'staff_id' not in request.session:
        return redirect('staffs:stafflogin')

    student = get_object_or_404(Student, roll_number=roll_number)
    
    # helper to get object or None
    def get_or_none(model, **kwargs):
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            return None

    # Importing models inside function to avoid circular imports if any, 
    # but preferably they should be at top. Let's assume they are available or import them.
    from students.models import (
        PersonalInfo, AcademicHistory, DiplomaDetails, UGDetails, PGDetails, 
        PhDDetails, ScholarshipInfo, StudentDocuments, BankDetails, OtherDetails
    )

    context = {
        'student': student,
        'personal_info': get_or_none(PersonalInfo, student=student),
        'academic_history': get_or_none(AcademicHistory, student=student),
        'diploma_details': get_or_none(DiplomaDetails, student=student),
        'ug_details': get_or_none(UGDetails, student=student),
        'pg_details': get_or_none(PGDetails, student=student),
        'phd_details': get_or_none(PhDDetails, student=student),
        'scholarship_info': get_or_none(ScholarshipInfo, student=student),
        'bank_details': get_or_none(BankDetails, student=student),
        'docs': get_or_none(StudentDocuments, student=student),
        'other_details': get_or_none(OtherDetails, student=student),
    }

    return render(request, 'staff/stud_detail.html', context)

def manage_semesters(request):
    if 'staff_id' not in request.session:
        return redirect('staffs:stafflogin')
    
    selected_semester = request.GET.get('semester')
    students = []
    
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        action = request.POST.get('action')

        if student_ids and action:
            from django.db.models import F
            
            if action == 'promote':
                # Only promote if current_semester <= 8. 
                # If they are already 9 (Course Completed), do not increment further.
                Student.objects.filter(roll_number__in=student_ids, current_semester__lte=8).update(current_semester=F('current_semester') + 1)
                messages.success(request, f"Successfully promoted selected students.")
            
            elif action == 'demote':
                # Only demote if current_semester > 1.
                Student.objects.filter(roll_number__in=student_ids, current_semester__gt=1).update(current_semester=F('current_semester') - 1)
                messages.success(request, f"Successfully demoted selected students.")
                
            return redirect(f"{request.path}?semester={selected_semester}") # Stay on same page
        else:
            messages.warning(request, "No students selected or invalid action.")

    display_semester_selector = True
    header_text = "Filter by Current Semester"

    # Restrict for Class Incharge
    try:
        current_staff = Staff.objects.get(staff_id=request.session['staff_id'])
        if current_staff.role == 'Class Incharge' and current_staff.assigned_semester:
            selected_semester = str(current_staff.assigned_semester)
            display_semester_selector = False
            header_text = f"Managing Semester {selected_semester} (Assigned)"
    except Staff.DoesNotExist:
        pass

    if selected_semester:
        students = Student.objects.filter(current_semester=selected_semester)
    
    return render(request, 'staff/manage_semesters.html', {
        'students': students, 
        'selected_semester': selected_semester,
        'display_semester_selector': display_semester_selector,
        'header_text': header_text
    })
