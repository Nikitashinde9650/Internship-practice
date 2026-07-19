from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# -------------------------------
# Employee Table
# -------------------------------
class Employee(db.Model):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    ename = db.Column(db.String(30), nullable=False)
    department = db.Column(db.String(30), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "ename": self.ename,
            "department": self.department,
            "salary": self.salary,
            "joining_date": str(self.joining_date),
            "email": self.email,
            "city": self.city
        }


# -------------------------------
# User Table
# -------------------------------
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