
@staff_login_required
def finalize_subject_performance(request, subject_id):
    from staffs.models import Subject
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Fetch all students who have marks for this subject
    # This assumes students are "enrolled" if they have a marks record
    enrolled_student_ids = StudentMarks.objects.filter(subject=subject).values_list('student_id', flat=True)
    students = Student.objects.filter(roll_number__in=enrolled_student_ids)
    
    archived_count = 0
    
    for student in students:
        # 1. Calculate Attendance %
        total_classes = StudentAttendance.objects.filter(student=student, subject=subject).count()
        present_classes = StudentAttendance.objects.filter(student=student, subject=subject, status='Present').count()
        attendance_percentage = round((present_classes / total_classes) * 100, 1) if total_classes > 0 else 0.0
        
        # 2. Get Internals & Calculate Grade Point
        try:
            marks_record = StudentMarks.objects.get(student=student, subject=subject)
            internal_marks = marks_record.internal_marks or 0
            
            # Simple Grade Point Logic (Scale of 10 based on Internal Marks assumed out of 100 or scaled)
            # Assuming Internal Marks is the proxy for Total Marks for this archival request
            score = internal_marks 
            
            if score >= 90: grade_point = 10
            elif score >= 80: grade_point = 9
            elif score >= 70: grade_point = 8
            elif score >= 60: grade_point = 7
            elif score >= 50: grade_point = 6
            else: grade_point = 0
            
            # 3. Update/Create StudentGPA Record
            # We use subject.semester as the target semester for this data
            student_gpa, created = StudentGPA.objects.get_or_create(student=student, semester=subject.semester)
            
            if not student_gpa.subject_data:
                student_gpa.subject_data = []
            
            # Remove existing entry for this subject to avoid duplicates
            student_gpa.subject_data = [entry for entry in student_gpa.subject_data if entry.get('subject_code') != subject.code]
            
            # Append new data
            new_entry = {
                'subject_code': subject.code,
                'subject_name': subject.name,
                'credits': getattr(subject, 'credits', 3), # Default to 3 if field missing/null
                'internal_marks': internal_marks,
                'attendance_percentage': attendance_percentage,
                'grade_point': grade_point,
                'archived_at': str(datetime.date.today())
            }
            student_gpa.subject_data.append(new_entry)
            
            # Recalculate Semester GPA
            total_points = 0
            total_credits = 0
            
            for entry in student_gpa.subject_data:
                creds = entry.get('credits', 3)
                gp = entry.get('grade_point', 0)
                total_points += (gp * creds)
                total_credits += creds
                
            student_gpa.gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
            student_gpa.total_credits = total_credits
            student_gpa.save()
            
            archived_count += 1
            
        except StudentMarks.DoesNotExist:
            continue
            
    messages.success(request, f"Archived data for {archived_count} students in {subject.name} - {subject.code}.")
    return redirect('staff_dashboard')
