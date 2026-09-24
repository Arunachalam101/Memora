"""
MEMORA Upload Handler - Phase 10A
Safe file upload handler for memory photos.
Supports development storage; can be swapped for cloud storage later.
"""

import os
import secrets
import mimetypes
from pathlib import Path
from flask import current_app


class UploadHandler:
    """Handle photo uploads for memory records"""
    
    # Configuration
    UPLOAD_FOLDER = 'static/uploads/memory'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    ALLOWED_MIMETYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp'
    }
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def init_app(app):
        """Initialize upload folder on app startup"""
        upload_path = Path(app.root_path) / UploadHandler.UPLOAD_FOLDER
        upload_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def validate_file(file):
        """
        Validate uploaded file before saving.
        
        Args:
            file: werkzeug.datastructures.FileStorage
        
        Returns:
            (is_valid, error_message)
        """
        
        # Check: file exists
        if not file or file.filename == '':
            return False, 'No file selected'
        
        # Check: file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size == 0:
            return False, 'File is empty'
        
        if file_size > UploadHandler.MAX_FILE_SIZE:
            return False, f'File too large (max {UploadHandler.MAX_FILE_SIZE // 1024 // 1024}MB)'
        
        # Check: extension whitelist
        filename = file.filename.lower()
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
        
        if ext not in UploadHandler.ALLOWED_EXTENSIONS:
            return False, f'Invalid file type (.{ext}). Allowed: {", ".join(UploadHandler.ALLOWED_EXTENSIONS)}'
        
        # Check: MIME type
        file.seek(0)
        mime_type, _ = mimetypes.guess_type(filename)
        
        if mime_type not in UploadHandler.ALLOWED_MIMETYPES:
            return False, f'Invalid MIME type: {mime_type}'
        
        file.seek(0)
        return True, None
    
    @staticmethod
    def save_file(file, patient_id, record_type):
        """
        Save file to disk with safe naming.
        
        Args:
            file: werkzeug.datastructures.FileStorage
            patient_id: int
            record_type: str ('person', 'place', or 'memory')
        
        Returns:
            (success, result) where result is path or error message
        """
        
        # Validate file first
        is_valid, error = UploadHandler.validate_file(file)
        if not is_valid:
            return False, error
        
        # Get file extension
        filename = file.filename.lower()
        ext = filename.rsplit('.', 1)[-1]
        
        # Generate safe filename (server-side, random, no user input)
        # Format: {patient_id}_{record_type}_{timestamp}_{random}.{ext}
        import time
        timestamp = int(time.time())
        random_suffix = secrets.token_hex(4)  # 8 random hex chars
        safe_filename = f'{patient_id}_{record_type}_{timestamp}_{random_suffix}.{ext}'
        
        # Build full path
        upload_path = Path(current_app.root_path) / UploadHandler.UPLOAD_FOLDER
        full_path = upload_path / safe_filename
        
        # Prevent path traversal (ensure file stays in upload folder)
        try:
            full_path.resolve().relative_to(upload_path.resolve())
        except ValueError:
            return False, 'Invalid file path'
        
        try:
            file.save(str(full_path))
            
            # Return relative path for database storage
            # Example: "/uploads/memory/1_person_1695484800_a7f3k8b2.jpg"
            relative_path = f'/uploads/memory/{safe_filename}'
            
            return True, relative_path
        
        except Exception as e:
            return False, f'Upload failed: {str(e)}'
    
    @staticmethod
    def delete_file(photo_path):
        """
        Delete photo from disk safely.
        
        Args:
            photo_path: str (relative path stored in database)
        
        Returns:
            (success, error_message)
        """
        
        if not photo_path:
            return True, None
        
        # Remove leading slash if present
        if photo_path.startswith('/'):
            photo_path = photo_path[1:]
        
        # Build full path
        full_path = Path(current_app.root_path) / photo_path
        
        # Prevent path traversal
        try:
            upload_folder = Path(current_app.root_path) / UploadHandler.UPLOAD_FOLDER
            full_path.resolve().relative_to(upload_folder.resolve())
        except ValueError:
            return False, 'Invalid file path'
        
        try:
            if full_path.exists():
                full_path.unlink()
            return True, None
        except Exception as e:
            return False, f'Delete failed: {str(e)}'
