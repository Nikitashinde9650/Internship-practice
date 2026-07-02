from config import db

class Employee(db.Model):

    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    ename = db.Column(db.String(30))
    department = db.Column(db.String(30))
    salary = db.Column(db.Integer)
    joining_date = db.Column(db.Date)

    def to_dict(self):
        return {
            "id": self.id,
            "ename": self.ename,
            "department": self.department,
            "salary": self.salary,
            "joining_date": str(self.joining_date)
        }