from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
    email = db.Column(db.String(100), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Active")
    password = db.Column(db.String(200), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    createdBy = db.Column(db.String(100))
    createdDate = db.Column(db.DateTime)
    updatedBy = db.Column(db.String(100))   
    updatedDate = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "ename": self.ename,
            "department": self.department,
            "salary": self.salary,
            "email": self.email,
            "city": self.city,
            "status": self.status
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
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default='users')   # admin or user
    profile_photo = db.Column(db.String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "gender": self.gender
        }
class ActivityLog(db.Model):

    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=True)

    user_email = db.Column(db.String(150))

    action = db.Column(db.String(50), nullable=False)

    description = db.Column(db.String(255))

    ip_address = db.Column(db.String(50))

    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )