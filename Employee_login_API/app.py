from flask import Flask, request, jsonify
from datetime import datetime
from config import Config
from models import db, Employee, User

app = Flask(__name__)

# -------------------------------
# Config
# -------------------------------
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# -------------------------------
# Home API
# -------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Employee Management REST API Running Successfully"
    })


# -------------------------------
# Get All Employees
# -------------------------------
@app.route("/employees", methods=["GET"])
def get_employees():

    employees = Employee.query.all()

    return jsonify([emp.to_dict() for emp in employees])


# -------------------------------
# Get Employee By ID
# -------------------------------
@app.route("/employees/<int:id>", methods=["GET"])
def get_employee(id):

    employee = db.session.get(Employee, id)

    if employee is None:
        return jsonify({
            "message": "Employee Not Found"
        }), 404

    return jsonify(employee.to_dict())


# -------------------------------
# Get All Users
# -------------------------------
@app.route("/users", methods=["GET"])
def get_users():

    users = User.query.all()

    return jsonify([user.to_dict() for user in users])


# -------------------------------
# Register API
# -------------------------------
@app.route("/register", methods=["POST"])
def register():

    try:

        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        address = data.get("address")
        city = data.get("city")
        gender = data.get("gender")

        if not name or not email or not password:
            return jsonify({
                "message": "Name, Email and Password are required"
            }), 400

        user = User.query.filter_by(email=email).first()

        if user:
            return jsonify({
                "message": "Email already exists"
            }), 400

        new_user = User(
            name=name,
            email=email,
            password=password,
            address=address,
            city=city,
            gender=gender
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User Registered Successfully"
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "message": str(e)
        }), 500


# -------------------------------
# Login API
# -------------------------------
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and Password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({
            "message": "User Not Found"
        }), 404

    if user.password != password:
        return jsonify({
            "message": "Invalid Password"
        }), 401

    return jsonify({
        "message": "Login Successful",
        "user": user.to_dict()
    })


# -------------------------------
# Logout API
# -------------------------------
@app.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "message": "Logout Successful"
    }), 200
# -------------------------------
# # -------------------------------
# Add Employee
# -------------------------------
@app.route("/employees", methods=["POST"])
def add_employee():

    try:

        data = request.get_json()

        ename = data.get("ename")
        department = data.get("department")
        salary = data.get("salary")
        joining_date = data.get("joining_date")
        email = data.get("email")
        city = data.get("city")

        # Validation
        if not ename or not department or salary is None or not joining_date or not email or not city:
            return jsonify({
                "message": "All fields are required"
            }), 400

        if float(salary) <= 0:
            return jsonify({
                "message": "Salary must be greater than 0"
            }), 400

        # Check duplicate email
        existing_employee = Employee.query.filter_by(email=email).first()

        if existing_employee:
            return jsonify({
                "message": "Employee Email already exists"
            }), 400

        joining_date = datetime.strptime(
            joining_date,
            "%Y-%m-%d"
        ).date()

        new_employee = Employee(
            ename=ename,
            department=department,
            salary=salary,
            joining_date=joining_date,
            email=email,
            city=city
        )

        db.session.add(new_employee)
        db.session.commit()

        return jsonify({
            "message": "Employee Added Successfully"
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "message": str(e)
        }), 500


# -------------------------------
# Update Employee
# -------------------------------
@app.route("/employees/<int:id>", methods=["PUT"])
def update_employee(id):

    try:

        employee = db.session.get(Employee, id)

        if employee is None:
            return jsonify({
                "message": "Employee Not Found"
            }), 404

        data = request.get_json()

        if "ename" in data:
            employee.ename = data["ename"]

        if "department" in data:
            employee.department = data["department"]

        if "salary" in data:

            if float(data["salary"]) <= 0:
                return jsonify({
                    "message": "Salary must be greater than 0"
                }), 400

            employee.salary = data["salary"]

        if "joining_date" in data:
            employee.joining_date = datetime.strptime(
                data["joining_date"],
                "%Y-%m-%d"
            ).date()

        if "email" in data:
            employee.email = data["email"]

        if "city" in data:
            employee.city = data["city"]

        db.session.commit()

        return jsonify({
            "message": "Employee Updated Successfully"
        })

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "message": str(e)
        }), 500


# -------------------------------
# Delete Employee
# -------------------------------
@app.route("/employees/<int:id>", methods=["DELETE"])
def delete_employee(id):

    try:

        employee = db.session.get(Employee, id)

        if employee is None:
            return jsonify({
                "message": "Employee Not Found"
            }), 404

        db.session.delete(employee)
        db.session.commit()

        return jsonify({
            "message": "Employee Deleted Successfully"
        })

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "message": str(e)
        }), 500


# -------------------------------
# Run Application
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)


