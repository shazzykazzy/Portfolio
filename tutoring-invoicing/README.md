# Tutoring Invoice Manager

A professional, full-featured invoicing application designed specifically for tutoring businesses. Built with Flask and SQLite, this application provides a clean, responsive interface for managing students, tracking sessions, generating invoices, and analyzing income.

## Features

### Core Functionality
- **Student Management**: Add, edit, and track students with customizable hourly rates
- **Session Tracking**: Log tutoring sessions with dates, duration, subjects, and notes
- **Invoice Generation**: Create professional invoices with automatic calculations
- **Payment Tracking**: Monitor paid/unpaid status and payment dates
- **PDF Export**: Generate professional PDF invoices with your business branding

### Dashboard
- Real-time overview of monthly and yearly revenue
- Outstanding payments tracking
- Quick access to recent sessions
- Active student count
- Unpaid invoice notifications

### Student Profiles
- Complete contact information (name, email, phone, address)
- Customizable hourly rates per student
- Full session history
- Payment history and totals

### Invoice Features
- Automatic invoice numbering (sequential)
- Link multiple sessions to one invoice
- GST/tax calculation (configurable rate)
- Professional PDF generation
- Mark invoices as paid with payment date tracking
- View unbilled sessions

### Reporting
- Income summary by month or year
- Outstanding invoices report with overdue tracking
- Export data to CSV (invoices and sessions)
- Detailed financial analytics

### Settings
- Customizable business information
- Payment details for invoices
- Tax rate configuration
- Multi-currency support (default: NZD)
- Professional business branding on invoices

## Technology Stack

- **Backend**: Python 3.x with Flask framework
- **Database**: SQLite (lightweight, serverless)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **PDF Generation**: ReportLab
- **Design**: Responsive, mobile-first design

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the application**
   ```bash
   cd tutoring-invoicing
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your web browser
   - Navigate to: `http://localhost:5000`
   - The application will automatically create the database on first run

## First Time Setup

1. **Configure Business Settings**
   - Click on "Settings" in the navigation menu
   - Enter your business name, contact information, and address
   - Add your bank account/payment details
   - Set your tax rate (default is 15% for NZ GST)
   - Choose your currency
   - Click "Save Settings"

2. **Add Your First Student**
   - Navigate to "Students"
   - Click "Add Student"
   - Fill in student details and hourly rate
   - Click "Save Student"

3. **Log Your First Session**
   - Go to "Sessions"
   - Click "Add Session"
   - Select the student, enter date, duration, and subject
   - Click "Save Session"

4. **Create Your First Invoice**
   - Navigate to "Invoices"
   - Click "Create Invoice"
   - Select a student with unbilled sessions
   - Check the sessions to include
   - Set issue and due dates
   - Click "Create Invoice"

## Usage Guide

### Managing Students

**Add a Student:**
1. Go to Students page
2. Click "Add Student"
3. Enter name, contact details, and hourly rate
4. Click "Save Student"

**Edit a Student:**
1. Find the student in the list
2. Click "Edit"
3. Update information
4. Click "Save Student"

**Delete a Student:**
1. Click "Delete" next to the student
2. Confirm the deletion

### Tracking Sessions

**Log a Session:**
1. Go to Sessions page
2. Click "Add Session"
3. Select student (rate auto-fills)
4. Enter date, duration, subject, and any notes
5. Click "Save Session"

**Filter Sessions:**
- Use the search box to find sessions
- Filter by student
- Filter by billed/unbilled status

### Creating Invoices

**Generate an Invoice:**
1. Go to Invoices page
2. Click "Create Invoice"
3. Select a student
4. Choose unbilled sessions to include
5. Set issue date and due date
6. Add optional notes
7. Click "Create Invoice"

**View Invoice:**
- Click "View" on any invoice
- See detailed invoice with all sessions
- Download as PDF
- Mark as paid

**Mark Invoice as Paid:**
1. Open the invoice
2. Click "Mark as Paid"
3. Payment date is automatically recorded

### Generating Reports

**Income Summary:**
1. Go to Reports page
2. Select "By Month" or "By Year"
3. View summarized income data
4. Export to CSV if needed

**Outstanding Invoices:**
- View all unpaid invoices
- See days overdue
- Track total outstanding amount

**Export Data:**
- Click "Export All Invoices" for complete invoice data
- Click "Export All Sessions" for session history
- Files download as CSV for Excel/Google Sheets

## File Structure

```
tutoring-invoicing/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                 # Git ignore rules
├── tutoring.db                # SQLite database (created on first run)
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── dashboard.html        # Dashboard page
│   ├── students.html         # Students management
│   ├── sessions.html         # Sessions tracking
│   ├── invoices.html         # Invoice management
│   ├── reports.html          # Reports and analytics
│   └── settings.html         # Application settings
└── static/                    # Static assets
    ├── css/
    │   └── style.css         # Application styles
    └── js/
        └── main.js           # JavaScript utilities
```

## Database Schema

The application uses SQLite with four main tables:

- **settings**: Business configuration and preferences
- **students**: Student information and rates
- **sessions**: Tutoring session records
- **invoices**: Invoice data and payment tracking

## Backup and Data Management

### Backing Up Your Data

**Database Backup:**
The entire application data is stored in `tutoring.db`. To backup:
1. Stop the application
2. Copy `tutoring.db` to a safe location
3. Store backups regularly (weekly recommended)

**CSV Export:**
- Use the Reports page to export invoices and sessions
- Provides human-readable backup format
- Can be opened in Excel or Google Sheets

### Restoring Data
1. Stop the application
2. Replace `tutoring.db` with your backup file
3. Restart the application

## Security Notes

- Change the `SECRET_KEY` in `app.py` for production use
- The application runs on localhost by default (safe for personal use)
- For internet-facing deployment, use proper authentication
- Keep regular backups of your database
- Don't commit `tutoring.db` to version control (already in .gitignore)

## Customization

### Changing Currency
1. Go to Settings
2. Select your preferred currency from the dropdown
3. All new invoices will use the selected currency

### Adjusting Tax Rate
1. Go to Settings
2. Enter tax rate as decimal (e.g., 0.15 for 15%)
3. Applies to all new invoices

### Invoice Numbering
- Invoices are automatically numbered sequentially
- Format: INV-00001, INV-00002, etc.
- To change prefix, modify settings table in database

## Troubleshooting

### Application won't start
- Ensure Python 3.7+ is installed: `python --version`
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify port 5000 is not in use

### PDF generation fails
- Ensure reportlab is installed: `pip install reportlab`
- Check for error messages in console
- Verify invoice has sessions attached

### Database errors
- Delete `tutoring.db` and restart (will reset all data)
- Check file permissions
- Ensure SQLite is available

### Sessions not appearing in invoice creation
- Verify sessions are not already billed
- Check that sessions belong to the selected student
- Refresh the page and try again

## Development

### Running in Development Mode
The application runs in debug mode by default, providing:
- Automatic reloading on code changes
- Detailed error messages
- Development server warnings

### Production Deployment
For production use:
1. Set `debug=False` in `app.py`
2. Change the `SECRET_KEY` to a secure random value
3. Use a production WSGI server (gunicorn, waitress)
4. Set up proper authentication if needed
5. Use HTTPS for security

## Support and Contributions

This is an open-source project designed for tutoring businesses. Feel free to:
- Customize for your needs
- Add new features
- Fix bugs
- Share improvements

## License

This project is provided as-is for personal and commercial use.

## Version History

**Version 1.0.0** - Initial Release
- Complete student management
- Session tracking
- Invoice generation
- PDF export
- Reporting and analytics
- Responsive web interface

## Credits

Built with:
- Flask - Web framework
- ReportLab - PDF generation
- SQLite - Database
- Modern CSS and JavaScript

---

**Happy Tutoring!** 🎓

For questions or issues, please refer to the troubleshooting section or check the code comments.
