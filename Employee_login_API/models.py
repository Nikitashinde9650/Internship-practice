from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Employee Table
class Employee(db.Model):
    __tablename__ = "employee"

    Emp_ID = db.Column(db.Integer, primary_key=True)
    Emp_Name = db.Column(db.String(100), nullable=False)
    Department_Name = db.Column(db.String(100), nullable=False)
    Salary = db.Column(db.Float, nullable=False)
    Joining_Date = db.Column(db.Date, nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    City = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "Emp_ID": self.Emp_ID,
            "Emp_Name": self.Emp_Name,
            "Department_Name": self.Department_Name,
            "Salary": self.Salary,
            "Joining_Date": str(self.Joining_Date),
            "Email": self.Email,
            "City": self.City
        }


# User Table
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    gender = db.Column(db.String(20))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "gender": self.gender
        }