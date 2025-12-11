from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'name', 'designation', 'role', 'assigned_semester', 'department')
    list_editable = ('role', 'assigned_semester')
    search_fields = ('staff_id', 'name', 'email')
    list_filter = ('role', 'department', 'designation')
    fieldsets = (
        ('Basic Info', {
            'fields': ('staff_id', 'name', 'email', 'photo')
        }),
        ('Role & Designation', {
            'fields': ('role', 'assigned_semester', 'salutation', 'designation', 'department')
        }),
        ('Professional Details', {
            'fields': ('qualification', 'specialization', 'experience')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'date_of_joining', 'address')
        }),
        ('Accomplishments', {
            'fields': ('academic_details', 'publications', 'awards_and_memberships')
        }),
        ('Permissions', {
            'fields': ('is_active',) # Removed password field for security, use set_password via custom form or shell if really needed via admin, but standard is fine
        }),
    )
