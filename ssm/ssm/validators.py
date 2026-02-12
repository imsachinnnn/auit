"""
File validators for upload restrictions.
"""
from django.core.exceptions import ValidationError


def validate_file_size(file):
    """
    Validate that uploaded file is not larger than 100KB.
    """
    max_size_kb = 100
    max_size_bytes = max_size_kb * 1024  # 100KB = 102400 bytes
    
    if file.size > max_size_bytes:
        raise ValidationError(
            f'File size must not exceed {max_size_kb}KB. '
            f'Current file size: {file.size / 1024:.1f}KB'
        )
