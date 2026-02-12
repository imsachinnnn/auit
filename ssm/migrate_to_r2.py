"""
Data Migration Script: Upload Existing Files to Cloudflare R2
==============================================================

This script migrates existing local files to Cloudflare R2 storage.
It uploads files and updates database records to point to R2 URLs.

Usage:
    python migrate_to_r2.py [--dry-run] [--verbose]

Options:
    --dry-run    : Show what would be migrated without actually uploading
    --verbose    : Show detailed progress information
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssm.settings')
django.setup()

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from students.models import StudentDocuments, LeaveRequest, ResultScreenshot
from staffs.models import (
    Staff, StaffAwardHonour, StaffSeminar, StaffStudentGuided,
    StaffLeaveRequest, ConferenceParticipation, JournalPublication,
    BookPublication
)


class R2Migrator:
    """Handles migration of files from local storage to R2."""
    
    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = {
            'total_files': 0,
            'uploaded': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Initialize R2 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    def log(self, message, force=False):
        """Print message if verbose mode is enabled."""
        if self.verbose or force:
            print(message)
    
    def generate_r2_key(self, instance, field_name, original_filename):
        """Generate R2 key using the model's upload_to logic."""
        field = instance._meta.get_field(field_name)
        upload_to = field.upload_to
        
        if callable(upload_to):
            # It's a function (correct way now)
            return upload_to(instance, original_filename)
        else:
            # It's a string (fallback or old way)
            import datetime
            return field.generate_filename(instance, original_filename)

    def upload_and_update(self, instance, field_name, local_path):
        """Upload file and update database record."""
        try:
            file_field = getattr(instance, field_name)
            original_filename = os.path.basename(file_field.name)
            
            # Generate new key using actual model logic
            r2_key = self.generate_r2_key(instance, field_name, original_filename)
            
            if self.dry_run:
                self.log(f"  [DRY RUN] Would upload: {local_path} -> {r2_key}")
                self.log(f"  [DRY RUN] Would update DB: {field_name} = {r2_key}")
                return True

            # Check/Upload to R2
            skip_upload = False
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=r2_key)
                self.log(f"  [SKIP] File exists in R2: {r2_key}")
                self.stats['skipped'] += 1
                skip_upload = True
            except ClientError:
                pass

            if not skip_upload:
                self.s3_client.upload_file(
                    str(local_path),
                    self.bucket_name,
                    r2_key,
                    ExtraArgs={'CacheControl': 'max-age=86400'}
                )
                self.log(f"  [UPLOADED] {r2_key}")
                self.stats['uploaded'] += 1

            # Update Database
            if file_field.name != r2_key:
                # We need to manually update the field to point to the new path
                # But we don't want to trigger file save/upload logic again
                # So we update using queryset update to avoid signals/storage interaction
                # OR we set attribute and save(update_fields=[...])
                
                # Careful: file_field.name is the relative path
                # We want to set it to r2_key
                setattr(instance, field_name, r2_key)
                instance.save(update_fields=[field_name])
                self.log(f"  [DB UPDATED] {field_name} -> {r2_key}")
            
            return True

        except Exception as e:
            self.log(f"  [ERROR] Processing {local_path}: {str(e)}", force=True)
            self.stats['errors'] += 1
            return False

    def migrate_student_documents(self):
        """Migrate student documents to R2."""
        self.log("\n=== Migrating Student Documents ===", force=True)
        
        docs = StudentDocuments.objects.all()
        for doc in docs:
            self.log(f"\nProcessing student: {doc.student.roll_number}")
            
            file_fields = [
                'student_photo', 'student_id_card', 'community_certificate',
                'aadhaar_card', 'first_graduate_certificate', 'sslc_marksheet',
                'hsc_marksheet', 'income_certificate', 'bank_passbook',
                'driving_license'
            ]
            
            for field_name in file_fields:
                file_field = getattr(doc, field_name)
                if file_field and file_field.name:
                    local_path = Path(settings.MEDIA_ROOT) / file_field.name
                    if local_path.exists():
                        self.stats['total_files'] += 1
                        self.upload_and_update(doc, field_name, local_path)
                    elif not file_field.name.startswith('students/'): # Check if not already migrated path
                         self.log(f"  [WARNING] Local file not found: {local_path}")

    def migrate_student_leave_documents(self):
        """Migrate student leave documents."""
        self.log("\n=== Migrating Student Leave Documents ===", force=True)
        leaves = LeaveRequest.objects.exclude(document='').exclude(document__isnull=True)
        for leave in leaves:
            self.stats['total_files'] += 1
            local_path = Path(settings.MEDIA_ROOT) / leave.document.name
            if local_path.exists():
                self.upload_and_update(leave, 'document', local_path)

    def migrate_result_screenshots(self):
        """Migrate result screenshots."""
        self.log("\n=== Migrating Result Screenshots ===", force=True)
        items = ResultScreenshot.objects.exclude(screenshot='').exclude(screenshot__isnull=True)
        for item in items:
            self.stats['total_files'] += 1
            local_path = Path(settings.MEDIA_ROOT) / item.screenshot.name
            if local_path.exists():
                self.upload_and_update(item, 'screenshot', local_path)

    def migrate_staff_photos(self):
        """Migrate staff photos."""
        self.log("\n=== Migrating Staff Photos ===", force=True)
        staffs = Staff.objects.exclude(photo='').exclude(photo__isnull=True)
        for staff in staffs:
            self.stats['total_files'] += 1
            local_path = Path(settings.MEDIA_ROOT) / staff.photo.name
            if local_path.exists():
                self.upload_and_update(staff, 'photo', local_path)

    def migrate_staff_portfolio_documents(self):
        """Migrate staff portfolio documents."""
        self.log("\n=== Migrating Staff Portfolio Documents ===", force=True)
        
        models_fields = [
            (StaffAwardHonour, 'supporting_document'),
            (StaffSeminar, 'supporting_document'),
            (StaffStudentGuided, 'supporting_document'),
            (ConferenceParticipation, 'supporting_document'),
            (JournalPublication, 'supporting_document'),
            (BookPublication, 'supporting_document'),
            (StaffLeaveRequest, 'document')
        ]
        
        for ModelClass, field_name in models_fields:
            self.log(f"\nProcessing {ModelClass.__name__}...")
            items = ModelClass.objects.exclude(**{f'{field_name}': ''}).exclude(**{f'{field_name}__isnull': True})
            for item in items:
                self.stats['total_files'] += 1
                try:
                    file_field = getattr(item, field_name)
                    local_path = Path(settings.MEDIA_ROOT) / file_field.name
                    if local_path.exists():
                        self.upload_and_update(item, field_name, local_path)
                except Exception as e:
                    self.log(f"Error processing item {item.id}: {e}")
    
    def _migrate_staff_document(self, obj, doc_type):
        pass # Deprecated by generic logic
    
    def run(self):
        """Run the complete migration."""
        print("\n" + "="*60)
        print("  Cloudflare R2 Migration Script")
        print("="*60)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No files will be uploaded\n")
        
        # Verify R2 connection
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✓ Connected to R2 bucket: {self.bucket_name}\n")
        except Exception as e:
            print(f"✗ Failed to connect to R2: {str(e)}")
            print("\nPlease check your R2 credentials in .env file")
            return
        
        # Run migrations
        self.migrate_student_documents()
        self.migrate_student_leave_documents()
        self.migrate_result_screenshots()
        self.migrate_staff_photos()
        self.migrate_staff_portfolio_documents()
        
        # Print summary
        print("\n" + "="*60)
        print("  Migration Summary")
        print("="*60)
        print(f"Total files found:    {self.stats['total_files']}")
        print(f"Successfully uploaded: {self.stats['uploaded']}")
        print(f"Skipped (existing):   {self.stats['skipped']}")
        print(f"Errors:               {self.stats['errors']}")
        print("="*60 + "\n")
        
        if not self.dry_run:
            print("✓ Migration complete!")
            print("\nNext steps:")
            print("1. Verify files are accessible in your application")
            print("2. Check a few student/staff profiles to confirm photos display")
            print("3. Once verified, you can delete local media files if desired")
        else:
            print("Run without --dry-run to perform actual migration")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate files to Cloudflare R2')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without uploading')
    parser.add_argument('--verbose', action='store_true', help='Show detailed progress')
    
    args = parser.parse_args()
    
    migrator = R2Migrator(dry_run=args.dry_run, verbose=args.verbose)
    migrator.run()
