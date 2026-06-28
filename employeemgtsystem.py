import mysql.connector

# Database Connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123",
        database="company"
    )

    cursor = conn.cursor()
    print("Database Connected Successfully")

except Exception as e:
    print("Connection Error:", e)


# ---------------- ADD EMPLOYEE ----------------

def add_employee():
    try:
        eid = int(input("Enter Employee ID : "))
        name = input("Enter Name : ")
        dept = input("Enter Department : ")
        salary = float(input("Enter Salary : "))
        joining = input("Enter Joining Date (YYYY-MM-DD): ")

        query = """
        INSERT INTO employee
        VALUES(%s,%s,%s,%s,%s)
        """

        values = (eid, name, dept, salary, joining)

        cursor.execute(query, values)
        conn.commit()

        print("Employee Added Successfully")

    except Exception as e:
        print("Error :", e)


# ---------------- VIEW EMPLOYEE ----------------

def view_employee():

    try:

        cursor.execute("SELECT * FROM employee")

        rows = cursor.fetchall()

        employee_list = []

        for row in rows:

            emp = {
                "ID": row[0],
                "Name": row[1],
                "Department": row[2],
                "Salary": row[3],
                "Joining Date": row[4]
            }

            employee_list.append(emp)

        if len(employee_list) == 0:
            print("No Employee Found")

        else:

            for emp in employee_list:

                print("-----------------------------")
                for key, value in emp.items():
                    print(key, ":", value)

    except Exception as e:
        print(e)


# ---------------- SEARCH EMPLOYEE ----------------

def search_employee():

    try:

        eid = int(input("Enter Employee ID : "))

        cursor.execute(
            "SELECT * FROM employee WHERE eid=%s",
            (eid,)
        )

        row = cursor.fetchone()

        if row:

            employee = {
                "ID": row[0],
                "Name": row[1],
                "Department": row[2],
                "Salary": row[3],
                "Joining Date": row[4]
            }

            print()

            for k, v in employee.items():
                print(k, ":", v)

        else:
            print("Employee Not Found")

    except Exception as e:
        print(e)


# ---------------- UPDATE ----------------

def update_employee():

    try:

        eid = int(input("Enter Employee ID : "))

        salary = float(input("Enter New Salary : "))

        cursor.execute(
            "UPDATE employee SET salary=%s WHERE eid=%s",
            (salary, eid)
        )

        conn.commit()

        if cursor.rowcount > 0:
            print("Employee Updated Successfully")
        else:
            print("Employee Not Found")

    except Exception as e:
        print(e)


# ---------------- DELETE ----------------

def delete_employee():

    try:

        eid = int(input("Enter Employee ID : "))

        cursor.execute(
            "DELETE FROM employee WHERE eid=%s",
            (eid,)
        )

        conn.commit()

        if cursor.rowcount > 0:
            print("Employee Deleted Successfully")
        else:
            print("Employee Not Found")

    except Exception as e:
        print(e)


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