from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.cache import never_cache
from .models import (
    Student, PersonalInfo, AcademicHistory, DiplomaDetails, UGDetails, PGDetails, 
    PhDDetails, ScholarshipInfo, StudentDocuments, BankDetails, OtherDetails, Caste
)
def prevhome(request): return render(request, 'prevhome.html')
def stdregister(request): return render(request, 'stdregister.html')
def registration_success(request): return render(request, 'success.html')

# --- Login / Dashboard / Logout not working---------------
#@never_cache
#@login_required
def stdlogin(request):
    #if request.user.is_authenticated:
     #   return redirect('student_dashboard')
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        password_from_form = request.POST.get('password')
        try:
            student = Student.objects.get(roll_number=roll_number)
            if check_password(password_from_form, student.password):
                request.session['student_roll_number'] = student.roll_number
                return redirect('student_dashboard')
            else: error = "Invalid credentials."
        except Student.DoesNotExist: error = "Invalid credentials."
        return render(request, 'stdlogin.html', {'error': error})
    return render(request, 'stdlogin.html')

def stafflogin(request):
    #if request.user.is_authenticated:
     #   return redirect('student_dashboard')
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        password_from_form = request.POST.get('password')
        try:
            student = Student.objects.get(roll_number=roll_number)
            if check_password(password_from_form, student.password):
                request.session['student_roll_number'] = student.roll_number
                return redirect('student_dashboard')
            else: error = "Invalid credentials."
        except Student.DoesNotExist: error = "Invalid credentials."
        return render(request, 'stdlogin.html', {'error': error})
    return render(request, 'stdlogin.html')

def student_dashboard(request):
    roll_number = request.session.get('student_roll_number')
    if roll_number:
        try:
            student = Student.objects.get(roll_number=roll_number)
            return render(request, 'stddash.html', {'student': student})
        except Student.DoesNotExist: pass
    return redirect('student_login')

def student_logout(request):
    try: del request.session['student_roll_number']
    except KeyError: pass
    return redirect('student_login')
def help_and_support(request):
    # You can add more context data here if needed
    return render(request, 'studhelp.html')
def exam_timetable(request):
    # You can pass timetable data from the database here in the future
    return render(request, 'timetable.html')

def student_editprofile(request):
    return render(request, 'studedit.html')

# --- API View for Registration (UPDATED) ---
@csrf_exempt
def register_student(request):
    all_castes = Caste.objects.all().order_by('name')
    context = {
        'all_castes': all_castes
    }
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = request.POST
        files = request.FILES
        
        hashed_password = make_password(data.get('password'))

        student = Student.objects.create(
            roll_number=data.get('roll_number'),
            register_number=data.get('register_number'),
            student_name=data.get('student_name'),
            student_email=data.get('student_email'),
            password=hashed_password,
            program_level=data.get('program_level'),
            ug_entry_type=data.get('ug_entry_type') if data.get('program_level') == 'UG' else ''
        )

        # --- CORRECTED LOGIC FOR SAVING CASTE ---
        # 1. Get the caste ID from the submitted form data
        caste_id = data.get('caste')
        caste_object = None # Start with an empty variable

        # 2. If an ID was submitted, find the Caste object in the database
        if caste_id:
            try:
                caste_object = Caste.objects.get(id=caste_id)
            except Caste.DoesNotExist:
                caste_object = None # If ID is invalid, do nothing

        

        # 3. Now, create the PersonalInfo object with the correct data
        PersonalInfo.objects.create(
            student=student,
            umis_id=data.get('umis_id'),
            emis_id=data.get('emis_id'),
            abc_id=data.get('abc_id'),
            date_of_birth=data.get('date_of_birth') or None,
            gender=data.get('gender'),
            blood_group=data.get('blood_group'),
            community=data.get('community'),
            
            # This is the correct way to save the relationship
            caste=caste_object, 
            
            religion=data.get('religion'),
            aadhaar_number=data.get('aadhaar_number'), 
            permanent_address=data.get('permanent_address'),
            present_address=data.get('present_address'),
            student_mobile=data.get('student_mobile'),
            father_name=data.get('father_name'),
            father_occupation=data.get('father_occupation'),
            father_mobile=data.get('father_mobile'),
            mother_name=data.get('mother_name'),
            mother_occupation=data.get('mother_occupation'),
            mother_mobile=data.get('mother_mobile'),
            parent_annual_income=data.get('parent_annual_income') or None,
            has_scholarship=data.get('has_scholarship') == 'yes'
        )

        BankDetails.objects.create(
            student=student, 
            account_holder_name=data.get('account_holder_name'),
            account_number=data.get('account_number'),
            bank_name=data.get('bank_name'), 
            branch_name=data.get('branch_name'),
            ifsc_code=data.get('ifsc_code'),
        )
        
        # ... (The rest of your view remains exactly the same) ...
        # (AcademicHistory, ScholarshipInfo, etc.)

        if data.get('has_scholarship') == 'yes':
            ScholarshipInfo.objects.create(
                student=student,
                is_first_graduate='is_first_graduate' in data,
                sch_bcmbc='sch_bcmbc' in data, sch_postmetric='sch_postmetric' in data,
                sch_pm='sch_pm' in data, sch_govt='sch_govt' in data,
                sch_pudhumai='sch_pudhumai' in data, sch_tamizh='sch_tamizh' in data,
                sch_private='sch_private' in data,
                private_scholarship_name=data.get('private_scholarship_name')
            )

        AcademicHistory.objects.create(
            student=student, 
            sslc_register_number=data.get('sslc_register_number'),
            sslc_percentage=data.get('sslc_percentage') or None, 
            sslc_year_of_passing=data.get('sslc_year_of_passing'),
            sslc_school_name=data.get('sslc_school_name'), 
            sslc_school_address=data.get('sslc_school_address'),
            hsc_register_number=data.get('hsc_register_number'),
            hsc_percentage=data.get('hsc_percentage') or None, 
            hsc_year_of_passing=data.get('hsc_year_of_passing'),
            hsc_school_name=data.get('hsc_school_name'), 
            hsc_school_address=data.get('hsc_school_address'),
        )

        program_level = data.get('program_level')
        
        if program_level == 'UG' and data.get('ug_entry_type') == 'Lateral':
            DiplomaDetails.objects.create(
                student=student, 
                diploma_register_number=data.get('diploma_register_number'), 
                diploma_percentage=data.get('diploma_percentage') or None, 
                diploma_year_of_passing=data.get('diploma_year_of_passing'), 
                diploma_college_name=data.get('diploma_college_name'), 
                diploma_college_address=data.get('diploma_college_address')
            )

        if program_level in ['PG', 'PHD']:
            UGDetails.objects.create(student=student, ug_course=data.get('ug_course'), ug_university=data.get('ug_university'), ug_ogpa=data.get('ug_ogpa') or None, ug_year_of_passing=data.get('ug_year_of_passing'))
        
        if program_level in ['PG', 'PHD']:
             PGDetails.objects.create(student=student, pg_course=data.get('pg_course'), pg_university=data.get('pg_university'), pg_ogpa=data.get('pg_ogpa') or None, pg_year_of_passing=data.get('pg_year_of_passing'))
        
        if program_level == 'PHD':
            PhDDetails.objects.create(student=student, phd_specialization=data.get('phd_specialization'), phd_university=data.get('phd_university'), phd_year_of_joining=data.get('phd_year_of_joining'))

        StudentDocuments.objects.create(
            student=student, student_photo=files.get('student_photo'), student_id_card=files.get('student_id_card'),
            community_certificate=files.get('community_certificate'), aadhaar_card=files.get('aadhaar_card'),
            first_graduate_certificate=files.get('first_graduate_certificate'), sslc_marksheet=files.get('sslc_marksheet'),
            hsc_marksheet=files.get('hsc_marksheet'), income_certificate=files.get('income_certificate'),
            bank_passbook=files.get('bank_passbook'), driving_license=files.get('driving_license'),
        )
        
        OtherDetails.objects.create(
            student=student, ambition=data.get('ambition'), role_model=data.get('role_model'),
            hobbies=data.get('hobbies'), identification_marks=data.get('identification_marks'),
        )

        return JsonResponse({'message': 'Registration successful!'}, status=201)

    except Exception as e:
        print(f"Error during registration: {e}")
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=400)
#@login_required
#def edit_profile(request):

    try:
        student = Student.objects.get(user=request.user)
        personal_info, _ = PersonalInfo.objects.get_or_create(student=student)
        student_docs, _ = StudentDocuments.objects.get_or_create(student=student)
    except Student.DoesNotExist:
        return redirect('student_login') 
    if request.method == 'POST':
        # --- Update Contact Info ---
        student.student_email = request.POST.get('student_email')
        personal_info.student_mobile = request.POST.get('student_mobile')
        personal_info.father_mobile = request.POST.get('father_mobile')
        personal_info.mother_mobile = request.POST.get('mother_mobile')

        # --- Update Documents (only if a new file is uploaded) ---
        if 'student_photo' in request.FILES:
            student_docs.student_photo = request.FILES['student_photo']
        
        if 'aadhaar_card' in request.FILES:
            student_docs.aadhaar_card = request.FILES['aadhaar_card']

        if 'community_certificate' in request.FILES:
            student_docs.community_certificate = request.FILES['community_certificate']

        if 'bank_passbook' in request.FILES:
            student_docs.bank_passbook = request.FILES['bank_passbook']
        
        # --- Save all the changes to the database ---
        student.save()
        personal_info.save()
        student_docs.save()

        # Provide feedback to the user and redirect
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('student_dashboard')

    else:
        
        context = {
            'student': student
        }
        return render(request, 'editprof.html', context    )
# --- CSRF Exemptions (no changes) ---
# students/views.py

from django.http import JsonResponse
from .models import Caste

def get_castes(request):
    """
    This view fetches a list of castes based on the community ID
    provided in the request's query parameters.
    """
    # 1. Get the community ID from the URL (e.g., /api/get-castes/?community_id=2)
    community_id = request.GET.get('community_id')

    # 2. If no ID is provided, return an empty list.
    if not community_id:
        return JsonResponse([], safe=False)

    # 3. Filter the Caste database table to find all castes that belong
    #    to the selected community.
    castes = Caste.objects.filter(community_id=community_id).values('id', 'name').order_by('name')

    # 4. Convert the results to a list and return it as a JSON response,
    #    which the JavaScript on the registration page can understand.
    return JsonResponse(list(castes), safe=False)
CSRF_TRUSTED_ORIGINS = ['https://a466adf.ngrok-free.app']

# In students/views.py
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
