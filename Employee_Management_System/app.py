from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,session
from datetime import datetime, timedelta
from config import Config
from sqlalchemy import func
from models import db, Employee, User
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

app = Flask(__name__)
app.config.from_object(Config)

# Session timeout apply
app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

jwt = JWTManager(app)
app.secret_key = "employee123"
# Session 30 minutes nantar expire hoil
app.permanent_session_lifetime = timedelta(minutes=30)


# Absolute upload folder path
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
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
@app.route("/register", methods=["POST"])
def register():

    try:

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        address = request.form.get("address")
        city = request.form.get("city")
        gender = request.form.get("gender")

        # Password hash kara
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter_by(email=email).first()
        role="user"

        if existing_user:
            return jsonify({
                "message": "Email already exists"
            }), 400

        user = User(
            name=name,
            email=email,
            password=hashed_password,
            address=address,
            city=city,
            gender=gender
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful. Please Login.", "success")
        return redirect(url_for("login_page"))

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": str(e)
        }), 500

# -------------------------------
# Dashboard
# -------------------------------

# -------------------------------
# Save Employee
# -------------------------------@app.route('/save-employee', methods=['POST'])
@app.route('/save-employee', methods=['POST'])
def save_employee():

    # Admin check
    if session.get('role') != 'admin':
        flash('Only admin can add employees', 'danger')
        return redirect(url_for('login_page'))

    ename = request.form.get('ename')
    department = request.form.get('department')
    salary = request.form.get('salary')
    joining_date = request.form.get('joining_date')
    email = request.form.get('email')
    city = request.form.get('city')
    status = request.form.get('status')
    password = request.form.get('password')

    # Logged-in user who is creating the record
    current_user = session.get('user_id')

    # 1️⃣ Employee table madhye save
    employee = Employee(
        ename=ename,
        department=department,
        salary=salary,
        joining_date=datetime.strptime(
            joining_date, '%Y-%m-%d'
        ).date(),
        email=email,
        city=city,
        status=status,

        # Audit fields
        createdBy=str(current_user),
        createdDate=datetime.now(),
        updatedBy=str(current_user),
        updatedDate=datetime.now()
    )

    db.session.add(employee)

    # 2️⃣ Users table madhye save
    existing_user = User.query.filter_by(email=email).first()

    if not existing_user:

        new_user = User(
            name=ename,
            email=email,
            password=generate_password_hash(password),
            city=city,
            role='user'
        )

        db.session.add(new_user)

    db.session.commit()

    flash('Employee Added Successfully', 'success')

    return redirect(url_for('employees_page'))
#------------update employee---------------
@app.route('/update-employee/<int:id>', methods=['POST'])
def update_employee(id):

    if session.get('role') != 'admin':
        flash('Access Denied', 'danger')
        return redirect(url_for('login_page'))

    employee = Employee.query.get_or_404(id)

    employee.ename = request.form.get('ename')
    employee.department = request.form.get('department')
    employee.salary = request.form.get('salary')
    employee.email = request.form.get('email')
    employee.city = request.form.get('city')
    current_user = session.get('user_id')
    employee.updatedBy = str(current_user)
    employee.updatedDate = datetime.now()

    db.session.commit()

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
@app.route("/employee-report")
def employee_report():

    employees = Employee.query.filter_by(is_deleted=False).all()

    return render_template(
        "employee_report.html",
        employees=employees
    )
#-----Department---------
from sqlalchemy import func
from flask import session, flash, redirect, render_template

@app.route("/dashboard")
def dashboard():

    # Login check
    if 'employee_id' not in session:
        flash('Please login first', 'danger')
        return redirect('/')

    # Total employees
    total_employees = Employee.query.count()

    # Total departments
    total_departments = db.session.query(
        func.count(func.distinct(Employee.department))
    ).scalar()

    # Active employees
    active_records = Employee.query.filter_by(status="Active").count()

    # Recent employees
    recent_employees = Employee.query.order_by(
        Employee.id.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        total_departments=total_departments,
        active_records=active_records,
        recent_employees=recent_employees
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


# Actual logout


# --------------Final logout action--------------------
@app.route('/do-logout', methods=['POST'])
def do_logout():

    session.clear()
    flash('Logout Successful', 'success')

    return redirect(url_for('login_page'))
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

        session.permanent = True

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['role'] = user.role

        flash('Login Successful', 'success')

        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    flash('Email id or password is incorrect', 'danger')
    return redirect(url_for('login_page'))
#--------------admin-dashboard--------------
@app.route('/admin-dashboard')
def admin_dashboard():

    # Admin check
    if session.get('role') != 'admin':
        flash('Access Denied', 'danger')
        return redirect(url_for('login_page'))

    # Total employees
    total_employees = Employee.query.count()

    # Total departments
    total_departments = db.session.query(
        func.count(func.distinct(Employee.department))
    ).scalar()

    # Active employees
    active_records = Employee.query.filter_by(status='Active').count()

    # Department wise employee count
    department_data = db.session.query(
    Employee.department,
    func.count(Employee.id)
).filter(Employee.is_deleted == False)\
 .group_by(Employee.department).all()

    labels = [d[0] for d in department_data]
    counts = [d[1] for d in department_data]

    return render_template(
        'dashboard.html',
        total_employees=total_employees,
        total_departments=total_departments,
        active_records=active_records,
        labels=labels,
        counts=counts
    )
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

    if file is None or file.filename == '':
        flash('Please select a photo', 'warning')
        return redirect(url_for('my_profile'))

    filename = secure_filename(file.filename)

    # ensure folder exists
   

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(file_path)

    user = User.query.get(session['user_id'])
    user.profile_photo = filename

    db.session.commit()

    flash('Photo uploaded successfully', 'success')

    return redirect(url_for('my_profile'))
#------------change password-
@app.route('/change-password', methods=['POST'])
def change_password():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = User.query.get(session['user_id'])

    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')

    if user.password != old_password:
        flash('Old password is incorrect', 'danger')
        return redirect(url_for('my_profile'))

    user.password = new_password
    db.session.commit()

    flash('Password Changed Successfully', 'success')

    return redirect(url_for('my_profile'))
#-------------forgot password-------------
@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')


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

    email = session.get('reset_email')

    user = User.query.filter_by(email=email).first()

    user.password = new_password

    db.session.commit()

    # Clear session OTP
    session.pop('reset_otp', None)
    session.pop('reset_email', None)

    flash('Password Reset Successfully', 'success')

    return redirect(url_for('login_page'))
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

    if session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login_page'))

    employee = Employee.query.get_or_404(id)

    # Soft delete
    employee.is_deleted = True
    employee.status = 'Inactive'
    employee.updatedBy = str(session.get('user_id'))
    employee.updatedDate = datetime.now()

    db.session.commit()

    flash('Employee moved to inactive list', 'success')
    return redirect(url_for('employees_page'))
# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)