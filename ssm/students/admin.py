from django.contrib import admin
from .models import (
    Student, PersonalInfo, AcademicHistory, DiplomaDetails, UGDetails, PGDetails,
    PhDDetails, ScholarshipInfo, StudentDocuments, BankDetails, OtherDetails,
    StudentSkill, StudentProject
)

class PersonalInfoInline(admin.StackedInline):
    model = PersonalInfo
    can_delete = False
    verbose_name_plural = 'Personal Information'
    extra = 0

class AcademicHistoryInline(admin.StackedInline):
    model = AcademicHistory
    can_delete = False
    verbose_name_plural = 'Academic History'
    extra = 0

class DiplomaDetailsInline(admin.StackedInline):
    model = DiplomaDetails
    can_delete = False
    verbose_name_plural = 'Diploma Details'
    extra = 0

class UGDetailsInline(admin.StackedInline):
    model = UGDetails
    can_delete = False
    verbose_name_plural = 'UG Details'
    extra = 0

class PGDetailsInline(admin.StackedInline):
    model = PGDetails
    can_delete = False
    verbose_name_plural = 'PG Details'
    extra = 0

class PhDDetailsInline(admin.StackedInline):
    model = PhDDetails
    can_delete = False
    verbose_name_plural = 'PhD Details'
    extra = 0

class ScholarshipInfoInline(admin.StackedInline):
    model = ScholarshipInfo
    can_delete = False
    verbose_name_plural = 'Scholarship Information'
    extra = 0

class StudentDocumentsInline(admin.StackedInline):
    model = StudentDocuments
    can_delete = False
    verbose_name_plural = 'Student Documents'
    extra = 0

class BankDetailsInline(admin.StackedInline):
    model = BankDetails
    can_delete = False
    verbose_name_plural = 'Bank Details'
    extra = 0

class OtherDetailsInline(admin.StackedInline):
    model = OtherDetails
    can_delete = False
    verbose_name_plural = 'Other Details'
    extra = 0

class StudentSkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 1

class StudentProjectInline(admin.StackedInline):
    model = StudentProject
    extra = 0

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'student_name', 'get_semester_display', 'program_level')
    search_fields = ('roll_number', 'student_name', 'student_email')
    list_filter = ('current_semester', 'program_level', 'ug_entry_type')
    actions = ['promote_students']
    
    inlines = [
        PersonalInfoInline,
        AcademicHistoryInline,
        DiplomaDetailsInline,
        UGDetailsInline,
        PGDetailsInline,
        PhDDetailsInline,
        ScholarshipInfoInline,
        StudentDocumentsInline,
        BankDetailsInline,
        OtherDetailsInline,
        StudentSkillInline,
        StudentProjectInline,
    ]

    @admin.display(description='Current Semester', ordering='current_semester')
    def get_semester_display(self, obj):
        if obj.current_semester > 8:
            return "Course Completed"
        return obj.current_semester

    @admin.action(description='Promote selected students to next semester')
    def promote_students(self, request, queryset):
        from django.db.models import F
        # Only promote students who are NOT yet completed (current_semester <= 8)
        # We allow 8 -> 9 (which becomes completed), but not 9 -> 10
        updated_count = queryset.filter(current_semester__lte=8).update(current_semester=F('current_semester') + 1)
        self.message_user(request, f"{updated_count} students were successfully promoted.")
