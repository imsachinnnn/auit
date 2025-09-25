from django import forms
from .models import Student

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        # This tells Django to create form fields for all fields in the Student model.
        fields = '__all__' 
        # You can also list them individually if you want to exclude some.
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This loop adds basic styling classes to each form field widget.
        # You can customize this to match your CSS framework.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control' # A generic class name

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

class StudentPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """Overrides the default method to find users in the Student model."""
        active_users = Student.objects.filter(
            student_email__iexact=email
        )
        return active_users

class StudentSetPasswordForm(SetPasswordForm):
    """
    This form works with any user model that has a `set_password` method,
    which we just added to your Student model.
    """
    pass