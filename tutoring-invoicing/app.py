"""
Tutoring Invoicing Application
A Flask-based application for managing tutoring sessions, students, and invoices
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import json
from io import BytesIO
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'tutoring.db'

# Database helper functions
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            business_email TEXT,
            business_phone TEXT,
            business_address TEXT,
            payment_details TEXT,
            tax_rate REAL DEFAULT 0.15,
            currency TEXT DEFAULT 'NZD',
            invoice_prefix TEXT DEFAULT 'INV',
            next_invoice_number INTEGER DEFAULT 1
        )
    ''')

    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            hourly_rate REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        )
    ''')

    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            session_date DATE NOT NULL,
            duration REAL NOT NULL,
            hourly_rate REAL NOT NULL,
            subject TEXT,
            notes TEXT,
            invoice_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')

    # Invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            student_id INTEGER NOT NULL,
            issue_date DATE NOT NULL,
            due_date DATE NOT NULL,
            subtotal REAL NOT NULL,
            tax_amount REAL NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'unpaid',
            payment_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # Insert default settings if not exists
    cursor.execute('SELECT COUNT(*) FROM settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO settings (business_name, business_email, business_phone,
                                business_address, payment_details, tax_rate, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('My Tutoring Business', 'tutor@example.com', '+64 21 123 4567',
              '123 Example Street, Auckland, New Zealand',
              'Bank: Example Bank\nAccount: 12-3456-7890123-00', 0.15, 'NZD'))

    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Routes
@app.route('/')
def index():
    """Dashboard view"""
    return render_template('dashboard.html')

@app.route('/api/dashboard-stats')
def dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db()
    cursor = conn.cursor()

    # Current month and year
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    current_year = now.year

    # Total revenue this month
    cursor.execute('''
        SELECT COALESCE(SUM(total_amount), 0) as monthly_revenue
        FROM invoices
        WHERE strftime('%Y-%m', issue_date) = ?
    ''', (current_month,))
    monthly_revenue = cursor.fetchone()['monthly_revenue']

    # Total revenue this year
    cursor.execute('''
        SELECT COALESCE(SUM(total_amount), 0) as yearly_revenue
        FROM invoices
        WHERE strftime('%Y', issue_date) = ?
    ''', (str(current_year),))
    yearly_revenue = cursor.fetchone()['yearly_revenue']

    # Outstanding payments
    cursor.execute('''
        SELECT COALESCE(SUM(total_amount), 0) as outstanding
        FROM invoices
        WHERE status = 'unpaid'
    ''')
    outstanding = cursor.fetchone()['outstanding']

    # Recent sessions (last 10)
    cursor.execute('''
        SELECT s.*, st.name as student_name
        FROM sessions s
        JOIN students st ON s.student_id = st.id
        ORDER BY s.session_date DESC, s.created_at DESC
        LIMIT 10
    ''')
    recent_sessions = [dict(row) for row in cursor.fetchall()]

    # Total students
    cursor.execute('SELECT COUNT(*) as total FROM students WHERE active = 1')
    total_students = cursor.fetchone()['total']

    # Unpaid invoices count
    cursor.execute('SELECT COUNT(*) as count FROM invoices WHERE status = "unpaid"')
    unpaid_invoices_count = cursor.fetchone()['count']

    conn.close()

    return jsonify({
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,
        'outstanding': outstanding,
        'recent_sessions': recent_sessions,
        'total_students': total_students,
        'unpaid_invoices_count': unpaid_invoices_count
    })

@app.route('/students')
def students():
    """Students list view"""
    return render_template('students.html')

@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    """Get all students or create new student"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('''
            SELECT s.*,
                   COUNT(DISTINCT se.id) as session_count,
                   COALESCE(SUM(se.duration * se.hourly_rate), 0) as total_earnings
            FROM students s
            LEFT JOIN sessions se ON s.id = se.student_id
            WHERE s.active = 1
            GROUP BY s.id
            ORDER BY s.name
        ''')
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(students)

    elif request.method == 'POST':
        data = request.json
        cursor.execute('''
            INSERT INTO students (name, email, phone, address, hourly_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['name'], data.get('email', ''), data.get('phone', ''),
              data.get('address', ''), data['hourly_rate'], data.get('notes', '')))
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': student_id, 'message': 'Student created successfully'}), 201

@app.route('/api/students/<int:student_id>', methods=['GET', 'PUT', 'DELETE'])
def api_student(student_id):
    """Get, update, or delete a specific student"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        if not student:
            conn.close()
            return jsonify({'error': 'Student not found'}), 404

        # Get sessions
        cursor.execute('''
            SELECT * FROM sessions
            WHERE student_id = ?
            ORDER BY session_date DESC
        ''', (student_id,))
        sessions = [dict(row) for row in cursor.fetchall()]

        # Get invoices
        cursor.execute('''
            SELECT * FROM invoices
            WHERE student_id = ?
            ORDER BY issue_date DESC
        ''', (student_id,))
        invoices = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return jsonify({
            'student': dict(student),
            'sessions': sessions,
            'invoices': invoices
        })

    elif request.method == 'PUT':
        data = request.json
        cursor.execute('''
            UPDATE students
            SET name = ?, email = ?, phone = ?, address = ?, hourly_rate = ?, notes = ?
            WHERE id = ?
        ''', (data['name'], data.get('email', ''), data.get('phone', ''),
              data.get('address', ''), data['hourly_rate'], data.get('notes', ''), student_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Student updated successfully'})

    elif request.method == 'DELETE':
        # Soft delete
        cursor.execute('UPDATE students SET active = 0 WHERE id = ?', (student_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Student deleted successfully'})

@app.route('/sessions')
def sessions():
    """Sessions list view"""
    return render_template('sessions.html')

@app.route('/api/sessions', methods=['GET', 'POST'])
def api_sessions():
    """Get all sessions or create new session"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('''
            SELECT s.*, st.name as student_name, i.invoice_number
            FROM sessions s
            JOIN students st ON s.student_id = st.id
            LEFT JOIN invoices i ON s.invoice_id = i.id
            ORDER BY s.session_date DESC, s.created_at DESC
        ''')
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(sessions)

    elif request.method == 'POST':
        data = request.json
        cursor.execute('''
            INSERT INTO sessions (student_id, session_date, duration, hourly_rate, subject, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['student_id'], data['session_date'], data['duration'],
              data['hourly_rate'], data.get('subject', ''), data.get('notes', '')))
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': session_id, 'message': 'Session created successfully'}), 201

@app.route('/api/sessions/<int:session_id>', methods=['GET', 'PUT', 'DELETE'])
def api_session(session_id):
    """Get, update, or delete a specific session"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session = cursor.fetchone()
        conn.close()
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        return jsonify(dict(session))

    elif request.method == 'PUT':
        data = request.json
        cursor.execute('''
            UPDATE sessions
            SET session_date = ?, duration = ?, hourly_rate = ?, subject = ?, notes = ?
            WHERE id = ?
        ''', (data['session_date'], data['duration'], data['hourly_rate'],
              data.get('subject', ''), data.get('notes', ''), session_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Session updated successfully'})

    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Session deleted successfully'})

@app.route('/invoices')
def invoices():
    """Invoices list view"""
    return render_template('invoices.html')

@app.route('/api/invoices', methods=['GET', 'POST'])
def api_invoices():
    """Get all invoices or create new invoice"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('''
            SELECT i.*, s.name as student_name
            FROM invoices i
            JOIN students s ON i.student_id = s.id
            ORDER BY i.issue_date DESC
        ''')
        invoices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(invoices)

    elif request.method == 'POST':
        data = request.json

        # Get settings for tax rate and invoice number
        cursor.execute('SELECT * FROM settings LIMIT 1')
        settings = dict(cursor.fetchone())

        # Calculate totals
        subtotal = data['subtotal']
        tax_amount = subtotal * settings['tax_rate']
        total_amount = subtotal + tax_amount

        # Generate invoice number
        invoice_number = f"{settings['invoice_prefix']}-{settings['next_invoice_number']:05d}"

        # Create invoice
        cursor.execute('''
            INSERT INTO invoices (invoice_number, student_id, issue_date, due_date,
                                 subtotal, tax_amount, total_amount, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_number, data['student_id'], data['issue_date'], data['due_date'],
              subtotal, tax_amount, total_amount, data.get('notes', ''), 'unpaid'))
        invoice_id = cursor.lastrowid

        # Update invoice number in settings
        cursor.execute('UPDATE settings SET next_invoice_number = next_invoice_number + 1')

        # Link sessions to invoice if provided
        if 'session_ids' in data:
            for session_id in data['session_ids']:
                cursor.execute('UPDATE sessions SET invoice_id = ? WHERE id = ?',
                             (invoice_id, session_id))

        conn.commit()
        conn.close()
        return jsonify({'id': invoice_id, 'invoice_number': invoice_number,
                       'message': 'Invoice created successfully'}), 201

@app.route('/api/invoices/<int:invoice_id>', methods=['GET', 'PUT', 'DELETE'])
def api_invoice(invoice_id):
    """Get, update, or delete a specific invoice"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('''
            SELECT i.*, s.name as student_name, s.email as student_email,
                   s.phone as student_phone, s.address as student_address
            FROM invoices i
            JOIN students s ON i.student_id = s.id
            WHERE i.id = ?
        ''', (invoice_id,))
        invoice = cursor.fetchone()
        if not invoice:
            conn.close()
            return jsonify({'error': 'Invoice not found'}), 404

        # Get sessions linked to this invoice
        cursor.execute('''
            SELECT * FROM sessions WHERE invoice_id = ? ORDER BY session_date
        ''', (invoice_id,))
        sessions = [dict(row) for row in cursor.fetchall()]

        # Get settings
        cursor.execute('SELECT * FROM settings LIMIT 1')
        settings = dict(cursor.fetchone())

        conn.close()
        return jsonify({
            'invoice': dict(invoice),
            'sessions': sessions,
            'settings': settings
        })

    elif request.method == 'PUT':
        data = request.json
        if 'status' in data and data['status'] == 'paid':
            cursor.execute('''
                UPDATE invoices
                SET status = ?, payment_date = ?
                WHERE id = ?
            ''', ('paid', data.get('payment_date', datetime.now().strftime('%Y-%m-%d')), invoice_id))
        else:
            cursor.execute('''
                UPDATE invoices
                SET due_date = ?, notes = ?
                WHERE id = ?
            ''', (data.get('due_date'), data.get('notes', ''), invoice_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Invoice updated successfully'})

    elif request.method == 'DELETE':
        # Unlink sessions first
        cursor.execute('UPDATE sessions SET invoice_id = NULL WHERE invoice_id = ?', (invoice_id,))
        cursor.execute('DELETE FROM invoices WHERE id = ?', (invoice_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Invoice deleted successfully'})

@app.route('/api/sessions/unbilled')
def unbilled_sessions():
    """Get sessions that haven't been invoiced yet"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, st.name as student_name
        FROM sessions s
        JOIN students st ON s.student_id = st.id
        WHERE s.invoice_id IS NULL
        ORDER BY st.name, s.session_date
    ''')
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(sessions)

@app.route('/reports')
def reports():
    """Reports view"""
    return render_template('reports.html')

@app.route('/api/reports/income')
def income_report():
    """Get income report data"""
    period = request.args.get('period', 'month')  # month or year
    conn = get_db()
    cursor = conn.cursor()

    if period == 'month':
        cursor.execute('''
            SELECT strftime('%Y-%m', issue_date) as period,
                   COUNT(*) as invoice_count,
                   SUM(subtotal) as subtotal,
                   SUM(tax_amount) as tax,
                   SUM(total_amount) as total
            FROM invoices
            GROUP BY strftime('%Y-%m', issue_date)
            ORDER BY period DESC
            LIMIT 12
        ''')
    else:
        cursor.execute('''
            SELECT strftime('%Y', issue_date) as period,
                   COUNT(*) as invoice_count,
                   SUM(subtotal) as subtotal,
                   SUM(tax_amount) as tax,
                   SUM(total_amount) as total
            FROM invoices
            GROUP BY strftime('%Y', issue_date)
            ORDER BY period DESC
        ''')

    report = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(report)

@app.route('/api/reports/outstanding')
def outstanding_report():
    """Get outstanding invoices report"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.*, s.name as student_name, s.email as student_email, s.phone as student_phone
        FROM invoices i
        JOIN students s ON i.student_id = s.id
        WHERE i.status = 'unpaid'
        ORDER BY i.due_date
    ''')
    outstanding = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(outstanding)

@app.route('/api/reports/export-csv')
def export_csv():
    """Export data to CSV"""
    report_type = request.args.get('type', 'income')
    conn = get_db()
    cursor = conn.cursor()

    if report_type == 'income':
        cursor.execute('''
            SELECT i.invoice_number, i.issue_date, s.name as student,
                   i.subtotal, i.tax_amount, i.total_amount, i.status, i.payment_date
            FROM invoices i
            JOIN students s ON i.student_id = s.id
            ORDER BY i.issue_date DESC
        ''')
    elif report_type == 'sessions':
        cursor.execute('''
            SELECT s.session_date, st.name as student, s.subject,
                   s.duration, s.hourly_rate,
                   (s.duration * s.hourly_rate) as amount,
                   CASE WHEN s.invoice_id IS NULL THEN 'No' ELSE 'Yes' END as invoiced
            FROM sessions s
            JOIN students st ON s.student_id = st.id
            ORDER BY s.session_date DESC
        ''')
    else:
        conn.close()
        return jsonify({'error': 'Invalid report type'}), 400

    rows = cursor.fetchall()
    conn.close()

    # Generate CSV
    import csv
    from io import StringIO

    output = StringIO()
    if rows:
        writer = csv.writer(output)
        # Write header
        writer.writerow(rows[0].keys())
        # Write data
        for row in rows:
            writer.writerow(row)

    # Convert to bytes for download
    csv_data = output.getvalue()
    output.close()

    return csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename="{report_type}_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    }

@app.route('/settings')
def settings():
    """Settings view"""
    return render_template('settings.html')

@app.route('/api/settings', methods=['GET', 'PUT'])
def api_settings():
    """Get or update settings"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM settings LIMIT 1')
        settings = dict(cursor.fetchone())
        conn.close()
        return jsonify(settings)

    elif request.method == 'PUT':
        data = request.json
        cursor.execute('''
            UPDATE settings SET
                business_name = ?,
                business_email = ?,
                business_phone = ?,
                business_address = ?,
                payment_details = ?,
                tax_rate = ?,
                currency = ?
            WHERE id = 1
        ''', (data['business_name'], data['business_email'], data['business_phone'],
              data['business_address'], data['payment_details'],
              data['tax_rate'], data['currency']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Settings updated successfully'})

@app.route('/api/invoice/<int:invoice_id>/pdf')
def generate_pdf(invoice_id):
    """Generate PDF for invoice"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors

        conn = get_db()
        cursor = conn.cursor()

        # Get invoice data
        cursor.execute('''
            SELECT i.*, s.name as student_name, s.email as student_email,
                   s.phone as student_phone, s.address as student_address
            FROM invoices i
            JOIN students s ON i.student_id = s.id
            WHERE i.id = ?
        ''', (invoice_id,))
        invoice = dict(cursor.fetchone())

        # Get sessions
        cursor.execute('''
            SELECT * FROM sessions WHERE invoice_id = ? ORDER BY session_date
        ''', (invoice_id,))
        sessions = [dict(row) for row in cursor.fetchall()]

        # Get settings
        cursor.execute('SELECT * FROM settings LIMIT 1')
        settings = dict(cursor.fetchone())

        conn.close()

        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30,
                              topMargin=30, bottomMargin=18)

        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
        )

        # Business header
        elements.append(Paragraph(settings['business_name'], title_style))
        elements.append(Paragraph(settings['business_address'].replace('\n', '<br/>'), styles['Normal']))
        elements.append(Paragraph(f"Email: {settings['business_email']}", styles['Normal']))
        elements.append(Paragraph(f"Phone: {settings['business_phone']}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Invoice title
        invoice_title = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#e74c3c'),
        )
        elements.append(Paragraph(f"INVOICE {invoice['invoice_number']}", invoice_title))
        elements.append(Spacer(1, 20))

        # Invoice details table
        invoice_details = [
            ['Issue Date:', invoice['issue_date']],
            ['Due Date:', invoice['due_date']],
            ['Status:', invoice['status'].upper()],
        ]

        if invoice['status'] == 'paid' and invoice['payment_date']:
            invoice_details.append(['Payment Date:', invoice['payment_date']])

        details_table = Table(invoice_details, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 20))

        # Bill to section
        elements.append(Paragraph('<b>Bill To:</b>', styles['Heading3']))
        elements.append(Paragraph(invoice['student_name'], styles['Normal']))
        if invoice['student_email']:
            elements.append(Paragraph(invoice['student_email'], styles['Normal']))
        if invoice['student_phone']:
            elements.append(Paragraph(invoice['student_phone'], styles['Normal']))
        if invoice['student_address']:
            elements.append(Paragraph(invoice['student_address'].replace('\n', '<br/>'), styles['Normal']))
        elements.append(Spacer(1, 20))

        # Sessions table
        session_data = [['Date', 'Subject', 'Duration (hrs)', 'Rate', 'Amount']]
        for session in sessions:
            amount = session['duration'] * session['hourly_rate']
            session_data.append([
                session['session_date'],
                session['subject'] or 'Tutoring Session',
                f"{session['duration']:.2f}",
                f"{settings['currency']} {session['hourly_rate']:.2f}",
                f"{settings['currency']} {amount:.2f}"
            ])

        session_table = Table(session_data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        session_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        elements.append(session_table)
        elements.append(Spacer(1, 20))

        # Totals table
        totals_data = [
            ['Subtotal:', f"{settings['currency']} {invoice['subtotal']:.2f}"],
            [f"Tax ({settings['tax_rate']*100:.0f}% GST):", f"{settings['currency']} {invoice['tax_amount']:.2f}"],
            ['<b>Total:</b>', f"<b>{settings['currency']} {invoice['total_amount']:.2f}</b>"],
        ]

        totals_table = Table(totals_data, colWidths=[5*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 30))

        # Payment details
        elements.append(Paragraph('<b>Payment Details:</b>', styles['Heading3']))
        elements.append(Paragraph(settings['payment_details'].replace('\n', '<br/>'), styles['Normal']))

        if invoice['notes']:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph('<b>Notes:</b>', styles['Heading3']))
            elements.append(Paragraph(invoice['notes'], styles['Normal']))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"invoice_{invoice['invoice_number']}.pdf"
        )

    except ImportError:
        return jsonify({
            'error': 'PDF generation requires reportlab. Install it with: pip install reportlab'
        }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
