# Student and Staff Management System (SSM)

SSM is a Django-based web application designed to manage student and staff data for an educational institution (specifically tailored for Annamalai University). It provides a comprehensive dashboard for students to manage their profiles, academic history, and documents, and for staff to manage their schedules, leave requests, and more.

## Features

### Student Module
- **Profile Management**: Detailed personal information, bank details, and contact info.
- **Academic History**: Records of SSLC, HSC, Diploma, UG, PG, and PhD details.
- **Document Management**: Upload and storage of student photos, certificates, and passbooks.
- **Scholarship Info**: Tracking of various scholarship eligibilities (First Graduate, BC/MBC, etc.).

### Staff Module
- **Role-Based Access**: Support for HOD, Class Incharge, and Course Incharge roles.
- **Subject Management**: Mapping of subjects to staff and semesters.
- **Timetable & Exam Schedule**: Management of class schedules and exam dates.
- **Leave Management System**: Workflow for staff to apply for leave (CL, Medical, etc.) and for HODs to approve/reject them.
- **News & Announcements**: Targeted announcements for Students, Staff, or All.

### Admin Portal
- Customized admin interface using `django-jazzmin` for a modern look and feel.
- Manage all models (Students, Staff, Subjects, etc.) directly.

## Technology Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript (Bootstrap 5 theme integration)
- **PDF Generation**: `xhtml2pdf` for generating reports/resumes.
- **AI Integration**: `google-genai` for AI-powered features (e.g., resume enhancement).
- **Email**: `django-anymail` (configured for Gmail SMTP/Resend).

## Installation & Setup

1.  **Clone the repository**
2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    ```
3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Variables**
    Create a `.env` file in the `ssm/` directory with the following keys:
    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    # Database config
    DB_NAME=ssm
    DB_USER=postgres
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432
    # Email config
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password
    # AI API
    GEMINI_API_KEY=your_gemini_key
    ```
5.  **Run Migrations**
    ```bash
    python manage.py migrate
    ```
6.  **Create Superuser**
    ```bash
    python manage.py createsuperuser
    ```
7.  **Run Server**
    ```bash
    python manage.py runserver
    ```

## Project Structure

- `ssm/`: Project configuration (settings, urls, wsgi).
- `students/`: App handling student-related functionality.
- `staffs/`: App handling staff-related functionality.
- `templates/`: Global HTML templates.
- `static/`: Static assets (CSS, JS, Images).
- `media/`: User-uploaded files.

## Contributors

- **Sachin** - *Initial Work*
