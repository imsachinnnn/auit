from django.contrib import admin
from .models import (
    Student, PersonalInfo, AcademicHistory, DiplomaDetails, UGDetails, PGDetails,
    PhDDetails, ScholarshipInfo, StudentDocuments, BankDetails, OtherDetails
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

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'student_name', 'student_email', 'program_level')
    search_fields = ('roll_number', 'student_name', 'student_email')
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
    ]
