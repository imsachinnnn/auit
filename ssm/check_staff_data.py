
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssm.settings')
django.setup()

from staffs.models import Staff

def check_staff_data():
    staffs = Staff.objects.all()
    print(f"Found {staffs.count()} staff members.")
    for staff in staffs:
        print(f"ID: {staff.staff_id}")
        print(f"  Name: {staff.name}")
        print(f"  Email: '{staff.email}'")
        print(f"  Qual: '{staff.qualification}'")
        print(f"  Spec: '{staff.specialization}'")
        print(f"  Address: '{staff.address}'")
        print("-" * 20)

if __name__ == "__main__":
    check_staff_data()
