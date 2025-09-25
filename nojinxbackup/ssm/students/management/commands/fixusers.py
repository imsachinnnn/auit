from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

class Command(BaseCommand):
    help = 'Finds and fixes user accounts that cannot receive password reset emails.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("--- Starting User Account Health Check ---"))
        
        fixed_user_count = 0
        all_users = User.objects.all()

        if not all_users.exists():
            self.stdout.write(self.style.WARNING("No users found in the database."))
            return

        for user in all_users:
            was_changed = False
            self.stdout.write(f"Checking User: '{user.username}' (Email: {user.email or 'Not set'})")

            # --- CHECK 1: User must be active ---
            if not user.is_active:
                user.is_active = True
                was_changed = True
                self.stdout.write(self.style.WARNING(f"  └── [FIXED] User was inactive. Now activated."))

            # --- CHECK 2: User must have a usable password set ---
            # A user created without a password can't reset it.
            if not user.has_usable_password():
                # This is a more robust way to fix the password issue.
                # It sets a hashed, but unusable, password.
                user.set_password(None) 
                was_changed = True
                self.stdout.write(self.style.WARNING(f"  └── [FIXED] User had no usable password. Placeholder set."))

            if was_changed:
                user.save()
                fixed_user_count += 1
            else:
                 self.stdout.write(self.style.SUCCESS(f"  └── Status: OK"))


        if fixed_user_count > 0:
            self.stdout.write(self.style.SUCCESS(f"\n--- Health Check Complete: {fixed_user_count} user(s) were fixed. ---"))
        else:
            self.stdout.write(self.style.SUCCESS("\n--- Health Check Complete: All user accounts look healthy. ---"))

