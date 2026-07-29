from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,session
from datetime import datetime
from config import Config
from models import db, Employee, User
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "employee123"

# -------------------------------
# Config
# -------------------------------
app.config.from_object(Config)

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
@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    print("EMAIL =", email)
    print("USER FOUND =", user)

    if user:
        print("DB PASSWORD =", user.password)
        print("CHECK =", check_password_hash(user.password, password))

    if user and check_password_hash(user.password, password):

        session['employee_id'] = user.id
        session['employee_name'] = user.name

        flash('Login Successful', 'success')
        return redirect(url_for('dashboard'))

    else:
        flash('Invalid Email or Password', 'danger')
        return redirect(url_for('login_page'))
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
# -------------------------------
@app.route("/save-employee", methods=["POST"])
def save_employee():

    ename = request.form.get("ename")
    department = request.form.get("department")
    salary = request.form.get("salary")
    joining_date = request.form.get("joining_date")
    email = request.form.get("email")
    city = request.form.get("city")
    status = request.form.get("status")

    employee = Employee(
        ename=ename,
        department=department,
        salary=salary,
        joining_date=datetime.strptime(joining_date, "%Y-%m-%d").date(),
        email=email,
        city=city,
        status=status,
    )

    db.session.add(employee)
    db.session.commit()

    flash("Employee Added Successfully", "success")

    return redirect(url_for("employees_page"))

@app.route("/update_employee/<int:id>", methods=["PUT"])
def update_employee(id):

    employee = Employee.query.get_or_404(id)

    data = request.get_json()

    employee.ename = data["name"]
    employee.department = data["department"]
    employee.salary = data["salary"]
    employee.email = data["email"]
    employee.city = data["city"]

    db.session.commit()

    return jsonify({"message":"Employee Updated Successfully"})

# -------------------------------
# Delete Employee
# -------------------------------

@app.route("/delete_employee/<int:id>", methods=["DELETE"])
def delete_employee(id):

    employee = Employee.query.get(id)

    if not employee:
        return jsonify({
            "message":"Employee not found"
        }),404


    db.session.delete(employee)
    db.session.commit()


    return jsonify({
        "message":"Employee Deleted Successfully"
    })



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

@app.route("/edit_employee")
def edit_employee():

    return render_template("edit_employee.html")

@app.route("/add_employee")
def add_employee():

    return render_template("add_employee.html")

#--------Add Employee------

@app.route("/employees-page")
def employees_page():

    employees = Employee.query.all()

    return render_template(
        "employees.html",
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

    total_employees = Employee.query.count()

    total_users = User.query.count()

    return render_template(
        "reports.html",
        total_employees=total_employees,
        total_users=total_users
    )
#------------total-employee card-----
@app.route("/employee-report")
def employee_report():

    employees = Employee.query.all()

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
def logout_page():
    return render_template('logout.html')

# Final logout action
@app.route('/do-logout', methods=['POST'])
def do_logout():

    session.clear()
    flash('Logout Successful', 'success')

    return redirect(url_for('login_page'))
# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)