from flask import Flask, request, jsonify
from config import Config
from models import db, Employee, User

app = Flask(__name__)

# Load Config
app.config.from_object(Config)

# Initialize DB
db.init_app(app)

# Create Tables
with app.app_context():
    db.create_all()


# -------------------------------
# Home
# -------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Employee Login API Running Successfully"
    })


# -------------------------------
# Get Employees
# -------------------------------
@app.route("/employees", methods=["GET"])
def get_employees():

    employees = Employee.query.all()

    return jsonify([emp.to_dict() for emp in employees])


# -------------------------------
# Get Users
# -------------------------------
@app.route("/users", methods=["GET"])
def get_users():

    users = User.query.all()

    return jsonify([user.to_dict() for user in users])


# -------------------------------
# Register
# -------------------------------
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    address = data.get("address")
    city = data.get("city")
    gender = data.get("gender")

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


# -------------------------------
# Login
# -------------------------------
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({
            "message": "User not found"
        }), 404

    if user.password != password:
        return jsonify({
            "message": "Invalid Password"
        }), 401

    return jsonify({
        "message": "Login Successful",
        "user": user.to_dict()
    })
@app.route("/logout", methods=["POST"])
def logout():
    return jsonify({
        "message": "Logout Successful"
    }), 200



if __name__ == "__main__":
    app.run(debug=True)