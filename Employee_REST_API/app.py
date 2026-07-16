from flask import Flask, request, jsonify
from models import db, Employee
from datetime import datetime
import config

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ===========================
# ADD EMPLOYEE
# ===========================
@app.route("/employee", methods=["POST"])
def add_employee():
    data = request.get_json()

    employee = Employee(
        ename=data["ename"],
        department=data["department"],
        salary=data["salary"],
        joining_date=datetime.strptime(
            data["joining_date"], "%Y-%m-%d"
        ).date(),
        email=data["email"],
        city=data["city"]
    )

    db.session.add(employee)
    db.session.commit()

    return jsonify({
        "message": "Employee Added Successfully"
    }), 201


# ===========================
# GET ALL EMPLOYEES
# ===========================
@app.route("/employees", methods=["GET"])
def get_all():

    employees = Employee.query.all()

    return jsonify([emp.to_dict() for emp in employees])


# ===========================
# SEARCH BY NAME
# ===========================
@app.route("/employee/search/name", methods=["GET"])
def search_name():

    name = request.args.get("name")

    employees = Employee.query.filter(
        Employee.ename.ilike(f"%{name}%")
    ).all()

    return jsonify([emp.to_dict() for emp in employees])


# ===========================
# SEARCH BY EMAIL
# ===========================
@app.route("/employee/search/email", methods=["GET"])
def search_email():

    email = request.args.get("email")

    employees = Employee.query.filter(
        Employee.email.ilike(f"%{email}%")
    ).all()

    return jsonify([emp.to_dict() for emp in employees])


# ===========================
# SEARCH BY DEPARTMENT
# ===========================
@app.route("/employee/search/department", methods=["GET"])
def search_department():

    department = request.args.get("department")

    employees = Employee.query.filter(
        Employee.department.ilike(f"%{department}%")
    ).all()

    return jsonify([emp.to_dict() for emp in employees])


# ===========================
# SEARCH BY CITY
# ===========================
@app.route("/employee/search/city", methods=["GET"])
def search_city():

    city = request.args.get("city")

    employees = Employee.query.filter(
        Employee.city.ilike(f"%{city}%")
    ).all()

    return jsonify([emp.to_dict() for emp in employees])


# ===========================
# PAGINATION
# ===========================
@app.route("/employees/page", methods=["GET"])
def pagination():

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=5, type=int)

    employees = Employee.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "current_page": page,
        "per_page": per_page,
        "total_records": employees.total,
        "employees": [emp.to_dict() for emp in employees.items]
    })


# ===========================
# SORT ASC
# ===========================
@app.route("/employees/sort/asc", methods=["GET"])
def sort_asc():

    employees = Employee.query.order_by(
        Employee.ename.asc()
    ).all()

    return jsonify([emp.to_dict() for emp in employees])


# ===========================
# SORT DESC
# ===========================
@app.route("/employees/sort/desc", methods=["GET"])
def sort_desc():

    employees = Employee.query.order_by(
        Employee.ename.desc()
    ).all()

    return jsonify([emp.to_dict() for emp in employees])


# ===========================
# HOME ROUTE
# ===========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Employee API is Running Successfully"
    })


if __name__ == "__main__":
    app.run(debug=True)