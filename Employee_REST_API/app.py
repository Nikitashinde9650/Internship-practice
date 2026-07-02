from flask import Flask, request, jsonify
from config import app, db
from models import Employee

with app.app_context():
    db.create_all()

@app.route("/")
@app.route("/employee", methods=["POST"])
def add_employee():

    data = request.get_json()
@app.route("/employee", methods=["GET"])
def get_all_employee():

    employees = Employee.query.all()

    result = []

    for emp in employees:
        result.append(emp.to_dict())

    return jsonify(result)
    employee = Employee(
        id=data["id"],
        ename=data["ename"],
        department=data["department"],
        salary=data["salary"],
        joining_date=data["joining_date"]
    )

    db.session.add(employee)
    db.session.commit()

    return jsonify({
        "message": "Employee Added Successfully"
    }), 201
def home():
    return "Employee REST API is Running..."
@app.route("/employee/<int:id>", methods=["GET"])
def get_employee(id):

    employee = Employee.query.get(id)

    if employee:
        return jsonify(employee.to_dict())

    return jsonify({"message": "Employee Not Found"}), 404

@app.route("/employee/<int:id>", methods=["PUT"])
def update_employee(id):

    employee = Employee.query.get(id)

    if employee:

        data = request.get_json()

        employee.ename = data["ename"]
        employee.department = data["department"]
        employee.salary = data["salary"]
        employee.joining_date = data["joining_date"]

        db.session.commit()

        return jsonify({"message": "Employee Updated Successfully"})

    return jsonify({"message": "Employee Not Found"}), 404

@app.route("/employee/<int:id>", methods=["DELETE"])
def delete_employee(id):

    employee = Employee.query.get(id)

    if employee:

        db.session.delete(employee)
        db.session.commit()

        return jsonify({"message": "Employee Deleted Successfully"})

    return jsonify({"message": "Employee Not Found"}), 404
if __name__ == "__main__":
    app.run(debug=True)