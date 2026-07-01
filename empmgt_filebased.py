import json
import os

FILE_NAME = "employee.json"

# ---------------- LOAD DATA ----------------

def load_data():
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except:
        return []


# ---------------- SAVE DATA ----------------

def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)


# ---------------- ADD EMPLOYEE ----------------

def add_employee():

    employees = load_data()

    try:
        eid = int(input("Enter Employee ID : "))

        # Duplicate ID Check
        for emp in employees:
            if emp["ID"] == eid:
                print("Employee ID Already Exists")
                return

        name = input("Enter Name : ")
        dept = input("Enter Department : ")
        salary = float(input("Enter Salary : "))
        joining = input("Enter Joining Date (YYYY-MM-DD): ")

        employee = {
            "ID": eid,
            "Name": name,
            "Department": dept,
            "Salary": salary,
            "Joining Date": joining
        }

        employees.append(employee)

        save_data(employees)

        print("Employee Added Successfully")

    except Exception as e:
        print("Error :", e)


# ---------------- VIEW EMPLOYEE ----------------

def view_employee():

    employees = load_data()

    if len(employees) == 0:
        print("No Employee Found")
        return

    for emp in employees:

        print("----------------------------")

        for key, value in emp.items():
            print(f"{key} : {value}")


# ---------------- SEARCH EMPLOYEE ----------------

def search_employee():

    employees = load_data()

    try:
        eid = int(input("Enter Employee ID : "))

        for emp in employees:

            if emp["ID"] == eid:

                print("----------------------------")
                for k, v in emp.items():
                    print(f"{k} : {v}")
                return

        print("Employee Not Found")

    except Exception as e:
        print("Error :", e)


# ---------------- UPDATE EMPLOYEE ----------------

def update_employee():

    employees = load_data()

    try:
        eid = int(input("Enter Employee ID : "))

        for emp in employees:

            if emp["ID"] == eid:

                emp["Salary"] = float(input("Enter New Salary : "))

                save_data(employees)

                print("Employee Updated Successfully")
                return

        print("Employee Not Found")

    except Exception as e:
        print("Error :", e)


# ---------------- DELETE EMPLOYEE ----------------

def delete_employee():

    employees = load_data()

    try:
        eid = int(input("Enter Employee ID : "))

        for emp in employees:

            if emp["ID"] == eid:

                employees.remove(emp)

                save_data(employees)

                print("Employee Deleted Successfully")
                return

        print("Employee Not Found")

    except Exception as e:
        print("Error :", e)


# ---------------- MENU ----------------

while True:

    print("\n========== Employee Management System ==========")
    print("1. Add Employee")
    print("2. View Employee")
    print("3. Search Employee")
    print("4. Update Employee")
    print("5. Delete Employee")
    print("6. Exit")

    choice = input("Enter Choice : ")

    if choice == "1":
        add_employee()

    elif choice == "2":
        view_employee()

    elif choice == "3":
        search_employee()

    elif choice == "4":
        update_employee()

    elif choice == "5":
        delete_employee()

    elif choice == "6":
        print("Thank You")
        break

    else:
        print("Invalid Choice")