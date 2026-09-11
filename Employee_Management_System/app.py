from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,session
from datetime import datetime, timedelta
from config import Config
from sqlalchemy import func
from models import db, User, Employee, ActivityLog
import csv
import io
from flask import make_response
import random
import os
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
def create_activity_log(action, description):

    user_id = session.get('user_id')
    user_email = session.get('user_email')

    ip_address = request.remote_addr

    log = ActivityLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        description=description,
        ip_address=ip_address,
        created_at=datetime.now()
    )

    db.session.add(log)
    db.session.commit()

app = Flask(__name__)
app.config.from_object(Config)

app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

jwt = JWTManager(app)

app.secret_key = "employee123"

app.permanent_session_lifetime = timedelta(minutes=30)

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    'static',
    'uploads'
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# -------------------------------
# Config
# -------------------------------
app.config.from_object(Config)

# Session timeout apply
app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)

db.init_app(app)

with app.app_context():
    db.create_all()

# -------------------------------
# Home Page
# -------------------------------
@app.route("/")
def home():
    return redirect(url_for("login_page"))


@app.route('/login-page')
def login_page():
    return render_template('login.html')
# -------------------------------
# Login Page
# -------------------------------

# -------------------------------
# Register Page
# -------------------------------
@app.route("/register-page")
def register_page():
    return render_template("register.html")
# -------------------------------
# Register API
# -------------------------------

# -------------------------------
# Dashboard
# -------------------------------

# -------------------------------
# register 
# -------------------------------@app.route('/save-employee', methods=['POST'])
@app.route("/register", methods=["POST"])
def register():

    try:
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        address = request.form.get("address")
        city = request.form.get("city")
        gender = request.form.get("gender")

        # Hash password
        hashed_password = generate_password_hash(password)

        # Check existing user
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return jsonify({
                "message": "Email already exists"
            }), 400

        # Create User
        user = User(
            name=name,
            email=email,
            password=hashed_password,
            address=address,
            city=city,
            gender=gender,
            role="user"
        )

        db.session.add(user)

        # Generate user ID
        db.session.flush()

        # REGISTER Activity Log
        log = ActivityLog(
            user_id=user.id,
            user_email=user.email,
            action="REGISTER",
            description="User registered successfully",
            ip_address=request.remote_addr,
            created_at=datetime.now()
        )

        db.session.add(log)

        # Save User + Activity Log
        db.session.commit()

        # Success message
        flash(
            "Registration Successful. Please Login.",
            "success"
        )

        return redirect(url_for("login_page"))

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "message": str(e)
        }), 500

# ---------------- SAVE EMPLOYEE ----------------
@app.route('/save-employee', methods=['POST'])
def save_employee():

    # Admin check
    if session.get('role') != 'admin':
        flash('Only admin can add employees', 'danger')
        return redirect(url_for('login_page'))

    try:

        # -------------------------------
        # 1. Get Form Data
        # -------------------------------

        ename = request.form.get('ename')
        department = request.form.get('department')
        salary = request.form.get('salary')
        joining_date = request.form.get('joining_date')
        email = request.form.get('email')
        city = request.form.get('city')
        status = request.form.get('status')
        password = request.form.get('password')

        # -------------------------------
        # 2. Create Employee
        # -------------------------------

        employee = Employee(
            ename=ename,
            department=department,
            salary=salary,
            joining_date=datetime.strptime(
                joining_date,
                '%Y-%m-%d'
            ).date(),
            email=email,
            city=city,
            status=status,

            # Audit Fields
            createdBy=str(session.get('user_email')),
            createdDate=datetime.now(),
            updatedBy=str(session.get('user_email')),
            updatedDate=datetime.now()
        )

        db.session.add(employee)

        # -------------------------------
        # 3. Create User Account
        # -------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if not existing_user:

            new_user = User(
                name=ename,
                email=email,
                password=generate_password_hash(password),
                city=city,
                role='user'
            )

            db.session.add(new_user)

        # -------------------------------
        # 4. Save Employee + User
        # -------------------------------

        db.session.commit()

        # -------------------------------
        # 5. CREATE Activity Log
        # -------------------------------

        create_activity_log(
            'CREATE',
            f'Employee "{ename}" created successfully'
        )

        # -------------------------------
        # 6. Success Message
        # -------------------------------

        flash(
            'Employee Added Successfully',
            'success'
        )

        return redirect(
            url_for('employees_page')
        )

    # -------------------------------
    # Error Handling
    # -------------------------------

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error while adding employee: {str(e)}',
            'danger'
        )

        return redirect(
            url_for('add_employee')
        )
#------------update employee---------------
@app.route('/update-employee/<int:id>', methods=['POST'])
def update_employee(id):

    # Admin check
    if session.get('role') != 'admin':
        flash('Access Denied', 'danger')
        return redirect(url_for('login_page'))

    # Get employee
    employee = Employee.query.get_or_404(id)

    # Update employee details
    employee.ename = request.form.get('ename')
    employee.department = request.form.get('department')
    employee.salary = request.form.get('salary')
    employee.email = request.form.get('email')
    employee.city = request.form.get('city')

    # Audit fields
    current_user = session.get('user_id')
    employee.updatedBy = str(current_user)
    employee.updatedDate = datetime.now()

    # Save changes
    db.session.commit()

    # Create UPDATE activity log
    create_activity_log(
        'UPDATE',
        f'Employee "{employee.ename}" updated successfully'
    )

    # Success message
    flash('Employee Updated Successfully', 'success')

    return redirect(url_for('employees_page'))
# -------------------------------
# Delete Employee
# -------------------------------


# -------------------------------
# Search Employee
# -------------------------------

@app.route("/search_employee", methods=["GET"])
def search_employee():

    name = request.args.get("name", "")

    employees = Employee.query.filter(
        Employee.ename.like(f"%{name}%")
    ).all()

    return jsonify([emp.to_dict() for emp in employees])

# -------------------------------
# Get Single Employee
# -------------------------------

@app.route("/get_employee/<int:id>")
def get_employee(id):

    employee = Employee.query.get_or_404(id)

    return jsonify(employee.to_dict())
# -------------------------------
# Edit Employee Page
# -------------------------------

@app.route('/edit-employee/<int:id>')
def edit_employee(id):

    if session.get('role') != 'admin':
        flash('Access Denied', 'danger')
        return redirect(url_for('login_page'))

    employee = Employee.query.get_or_404(id)

    return render_template('edit_employee.html', employee=employee)
#-----------add employee-------------------
@app.route('/add_employee')
def add_employee():

    # Fakt admin la access
    if session.get('role') != 'admin':
        flash('Only admin can add employees', 'danger')
        return redirect(url_for('user_dashboard'))

    return render_template('add_employee.html')

#--------Add Employee------

@app.route('/employees-page')
def employees_page():

    # Login check
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login_page'))

    employees = Employee.query.filter_by(is_deleted=False).all()

    return render_template(
        'employees.html',
        employees=employees
    )

# ------------User ---------

@app.route("/users")
def users():

    users = User.query.all()

    return render_template(
        "users.html",
        users=users
    )

#---------Report--------

@app.route("/reports")
def reports():

    total_employees = Employee.query.filter_by(is_deleted=False).count()

    total_users = User.query.count()

    return render_template(
        "reports.html",
        total_employees=total_employees,
        total_users=total_users
    )
#------------total-employee card-----
@app.route('/employee-report')
def employee_report():

    if session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login_page'))

    employees = Employee.query.filter_by(
        is_deleted=False
    ).all()

    return render_template(
        'employee_report.html',
        employees=employees
    )
#------------------user report-----------------
@app.route('/user-report')
def user_report():

    if session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login_page'))

    users = User.query.all()

    return render_template(
        'user_report.html',
        users=users
    )
#-----Department---------
from sqlalchemy import func
from flask import session, flash, redirect, render_template

@app.route("/dashboard")
def dashboard():

    # Admin login check
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access Denied', 'danger')
        return redirect(url_for('login_page'))

    # Total employees
    total_employees = Employee.query.filter_by(
        is_deleted=False
    ).count()

    # Total departments
    total_departments = db.session.query(
        func.count(func.distinct(Employee.department))
    ).filter(
        Employee.is_deleted == False
    ).scalar()

    # Active employees
    active_records = Employee.query.filter_by(
        status="Active",
        is_deleted=False
    ).count()

    # Recent employees
    recent_employees = Employee.query.filter_by(
        is_deleted=False
    ).order_by(
        Employee.id.desc()
    ).limit(5).all()

    # Department-wise employee count
    department_data = db.session.query(
        Employee.department,
        func.count(Employee.id)
    ).filter(
        Employee.is_deleted == False
    ).group_by(
        Employee.department
    ).all()

    # Chart data
    labels = [item[0] for item in department_data]
    counts = [item[1] for item in department_data]

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        total_departments=total_departments,
        active_records=active_records,
        recent_employees=recent_employees,
        labels=labels,
        counts=counts
    )
#----------DEpartment route------
@app.route("/department-report")
def department_report():

    employees = Employee.query.order_by(Employee.department).all()

    return render_template(
        "department_report.html",
        employees=employees
    )
#-------------Active Records---------
@app.route("/active-records")
def active_records():

    employees = Employee.query.filter_by(status="Active").all()

    return render_template(
        "active_records.html",
        employees=employees
    )
#-------------logout-----------------
# Logout confirmation page
@app.route('/logout')
def logout():
    return render_template('logout.html')


#------------- Actual logout----------------
@app.route('/do-logout', methods=['POST'])
def do_logout():

    # User login आहे का check करा
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    # Logout करण्यापूर्वी Activity Log तयार करा
    create_activity_log(
        'LOGOUT',
        'User logged out successfully'
    )

    # आता session clear करा
    session.clear()

    flash('Logout Successful', 'success')

    return redirect(url_for('login_page'))
# --------------Final logout action--------------------
@app.route('/login', methods=['POST'])
def login():

    email = request.form.get('email')
    password = request.form.get('password')

    # User shodha
    user = User.query.filter_by(email=email).first()

    if user and (
        check_password_hash(user.password, password)
        or user.password == password
    ):

        # Session create
        session.permanent = True

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['role'] = user.role

        # Activity Log
        create_activity_log(
            'LOGIN',
            'User logged in successfully'
        )

        flash('Login Successful', 'success')

        # Role-based dashboard
        if user.role == 'admin':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    flash('Email id or password is incorrect', 'danger')
    return redirect(url_for('login_page'))
#--------------user dashboard-------------
@app.route('/user-dashboard')
def user_dashboard():

    if session.get('role') != 'user':
        flash('Access Denied', 'danger')
        return redirect(url_for('login_page'))

    total_employees = Employee.query.count()

    total_departments = db.session.query(
        func.count(func.distinct(Employee.department))
    ).scalar()

    active_records = Employee.query.filter_by(status='Active').count()

    department_data = db.session.query(
        Employee.department,
        func.count(Employee.id)
    ).group_by(Employee.department).all()

    labels = [d[0] for d in department_data]
    counts = [d[1] for d in department_data]

    return render_template(
        'user_dashboard.html',
        total_employees=total_employees,
        total_departments=total_departments,
        active_records=active_records,
        labels=labels,
        counts=counts
    )
#----------my profile-----------
@app.route('/my-profile')
def my_profile():

    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])

    return render_template('my_profile.html', user=user)
#--------------update profile----------------
@app.route('/update-profile', methods=['POST'])
def update_profile():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])

    user.name = request.form.get('name')
    user.city = request.form.get('city')
    user.address = request.form.get('address')

    db.session.commit()

    flash('Profile Updated Successfully', 'success')

    return redirect(url_for('my_profile'))
#-----------------upload photo------------
@app.route('/upload-photo', methods=['POST'])
def upload_photo():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    file = request.files.get('photo')

    if not file or file.filename == '':
        flash('Please select a photo', 'danger')
        return redirect(url_for('my_profile'))

    upload_folder = os.path.join(
        app.root_path,
        'static',
        'uploads'
    )

    # Create uploads folder if it does not exist
    if not os.path.isdir(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)

    filename = file.filename

    file_path = os.path.join(
        upload_folder,
        filename
    )

    file.save(file_path)

    user = User.query.get(session['user_id'])
    user.profile_photo = filename

    db.session.commit()

    flash('Profile photo uploaded successfully', 'success')

    return redirect(url_for('my_profile'))
#------------change password-
@app.route('/change-password', methods=['POST'])
def change_password():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])

    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('my_profile'))

    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Check all fields
    if not old_password or not new_password or not confirm_password:
        flash('Please fill all password fields', 'warning')
        return redirect(url_for('my_profile'))

    # Check old password
    old_password_correct = False

    try:
        old_password_correct = check_password_hash(
            user.password,
            old_password
        )
    except Exception:
        old_password_correct = False

    # Support old plain-text passwords also
    if not old_password_correct and user.password == old_password:
        old_password_correct = True

    if not old_password_correct:
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('my_profile'))

    # Check new password confirmation
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('my_profile'))

    # Don't allow same password
    if old_password == new_password:
        flash('New password must be different from current password', 'warning')
        return redirect(url_for('my_profile'))

    # Save new password as hashed password
    user.password = generate_password_hash(new_password)

    db.session.commit()

    # Activity log
    create_activity_log(
        'PASSWORD CHANGE',
        'User password changed successfully'
    )

    flash('Password Changed Successfully', 'success')

    return redirect(url_for('my_profile'))

#--------OTP send-----------------


@app.route('/send-otp', methods=['POST'])
def send_otp():

    email = request.form.get('email')

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('Email not found', 'danger')
        return redirect(url_for('forgot_password'))

    otp = random.randint(100000, 999999)

    session['reset_otp'] = str(otp)
    session['reset_email'] = email

    # Demo purpose
    print('OTP:', otp)

    flash('OTP generated. Check terminal.', 'success')

    return redirect(url_for('reset_password'))
#---------------reset password------------------
@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')

#------------reset passwprd submit---------------
@app.route('/reset-password-submit', methods=['POST'])
def reset_password_submit():

    otp = request.form.get('otp')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # OTP check
    if otp != session.get('reset_otp'):
        flash('Invalid OTP', 'danger')
        return redirect(url_for('reset_password'))

    # Password match check
    if new_password != confirm_password:
        flash('Passwords do not match', 'danger')
        return redirect(url_for('reset_password'))

    # Get email from session
    email = session.get('reset_email')

    if not email:
        flash('Reset session expired. Please try again.', 'danger')
        return redirect(url_for('reset_password'))

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('reset_password'))

    # Hash new password
    user.password = generate_password_hash(new_password)

    db.session.commit()

    # Activity Log
    create_activity_log(
        'PASSWORD RESET',
        f'Password reset successfully for {email}'
    )

    # Clear reset session
    session.pop('reset_otp', None)
    session.pop('reset_email', None)

    flash('Password Reset Successfully', 'success')

    return redirect(url_for('login_page'))

#---------------forgot password---------------
@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

#---------------JWT API Tocken-------------
@app.route('/api/login', methods=['POST'])
def api_login():

    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        return jsonify({'message': 'Invalid email or password'}), 401

    identity_data = {
        'id': user.id,
        'email': user.email,
        'role': user.role
    }

    access_token = create_access_token(identity=identity_data)

    refresh_token = create_refresh_token(identity=identity_data)

    return jsonify({
        'message': 'Login Successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'role': user.role
    }), 200
#----JWT Protected route-------------
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def api_profile():

    current_user = get_jwt_identity()

    return jsonify({
        'message': 'Protected Route Accessed',
        'user': current_user
    }), 200
#------------admin protected route----------
@app.route('/api/admin-only', methods=['GET'])
@jwt_required()
def admin_only():

    current_user = get_jwt_identity()

    if current_user['role'] != 'admin':
        return jsonify({'message': 'Admin access required'}), 403

    return jsonify({
        'message': 'Welcome Admin',
        'user': current_user
    }), 200
#-----refresh tocken------------------
@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():

    current_user = get_jwt_identity()

    new_access_token = create_access_token(identity=current_user)

    return jsonify({
        'access_token': new_access_token
    }), 200
#-------------temporary delete employee----------
@app.route('/delete-employee/<int:id>')
def delete_employee(id):

    # Admin check
    if session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login_page'))

    # Get employee
    employee = Employee.query.get_or_404(id)

    # Store employee name before update
    employee_name = employee.ename

    # Soft delete
    employee.is_deleted = True
    employee.status = 'Inactive'

    # Audit fields
    employee.updatedBy = str(session.get('user_id'))
    employee.updatedDate = datetime.now()

    # Save changes
    db.session.commit()

    # Create DELETE activity log
    create_activity_log(
        'DELETE',
        f'Employee "{employee_name}" deleted successfully'
    )

    # Success message
    flash('Employee moved to inactive list', 'success')

    return redirect(url_for('employees_page'))

# ---------------- ACTIVITY LOGS API ----------------
@app.route('/api/activity-logs', methods=['GET'])
def get_activity_logs():

    # Only Admin can access activity logs
    if session.get('role') != 'admin':
        return jsonify({
            'message': 'Access denied'
        }), 403

    # Get all logs, latest first
    logs = ActivityLog.query.order_by(
        ActivityLog.id.desc()
    ).all()

    result = []

    for log in logs:

        result.append({
            'id': log.id,
            'user_id': log.user_id,
            'user_email': log.user_email,
            'action': log.action,
            'description': log.description,
            'ip_address': log.ip_address,
            'created_at': log.created_at.strftime(
                '%Y-%m-%d %H:%M:%S'
            )
        })

    return jsonify(result), 200
#-------------Activity- logs--------------------------

@app.route('/activity-logs')
def activity_logs():

    if session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login_page'))

    # Search values
    email = request.args.get('email', '').strip()
    action = request.args.get('action', '').strip()
    date = request.args.get('date', '').strip()

    # Page number
    page = request.args.get('page', 1, type=int)

    # Base query
    query = ActivityLog.query

    # Email filter
    if email:
        query = query.filter(
            ActivityLog.user_email.ilike(f'%{email}%')
        )

    # Action filter
    if action:
        query = query.filter(
            ActivityLog.action == action
        )

    # Date filter
    if date:
        query = query.filter(
            db.func.date(ActivityLog.created_at) == date
        )

    # Pagination
    pagination = query.order_by(
        ActivityLog.id.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    logs = pagination.items

    return render_template(
        'activity_logs.html',
        logs=logs,
        pagination=pagination,
        email=email,
        action=action,
        date=date
    )
#---------------export-activity/ csv-----------------

@app.route('/export-activity-logs')
def export_activity_logs():

    if session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login_page'))

    # Get filters
    email = request.args.get('email', '').strip()
    action = request.args.get('action', '').strip()
    date = request.args.get('date', '').strip()

    # Base query
    query = ActivityLog.query

    # Email filter
    if email:
        query = query.filter(
            ActivityLog.user_email.ilike(f'%{email}%')
        )

    # Action filter
    if action:
        query = query.filter(
            ActivityLog.action == action
        )

    # Date filter
    if date:
        query = query.filter(
            db.func.date(ActivityLog.created_at) == date
        )

    # Get all filtered logs
    logs = query.order_by(
        ActivityLog.id.desc()
    ).all()

    # Create CSV
    output = io.StringIO()

    writer = csv.writer(output)

    # Header
    writer.writerow([
        'ID',
        'User ID',
        'User Email',
        'Action',
        'Description',
        'IP Address',
        'Date & Time'
    ])

    # Data
    for log in logs:

        writer.writerow([
            log.id,
            log.user_id,
            log.user_email,
            log.action,
            log.description,
            log.ip_address,
            log.created_at
        ])

    # Response
    response = make_response(output.getvalue())

    response.headers['Content-Disposition'] = (
        'attachment; filename=activity_logs.csv'
    )

    response.headers['Content-Type'] = 'text/csv'

    return response

@app.route('/change-password-page')
def change_password_page():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    return render_template('change_password.html')
# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)