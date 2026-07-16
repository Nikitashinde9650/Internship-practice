from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    ename = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)

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