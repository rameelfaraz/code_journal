import psycopg
from config import DB_PASSWORD


def get_connection():
    return psycopg.connect(
        host="localhost",
        dbname="employee_analytics",
        user="postgres",
        password=DB_PASSWORD
    )


def total_employees(cur):
    cur.execute("SELECT COUNT(*) FROM employees;")
    return cur.fetchone()[0]


def salary_stats(cur):
    cur.execute("""
        SELECT AVG(salary), MAX(salary), MIN(salary), SUM(salary)
        FROM employees;
    """)
    return cur.fetchone()


def employees_per_department(cur):
    cur.execute("""
        SELECT department, COUNT(*)
        FROM employees
        GROUP BY department
        ORDER BY department;
    """)
    return cur.fetchall()


def avg_salary_per_department(cur):
    cur.execute("""
        SELECT department, AVG(salary)
        FROM employees
        GROUP BY department
        ORDER BY department;
    """)
    return cur.fetchall()


def city_distribution(cur):
    cur.execute("""
        SELECT city, COUNT(*)
        FROM employees
        GROUP BY city
        ORDER BY city;
    """)
    return cur.fetchall()


def distinct_cities(cur):
    cur.execute("SELECT DISTINCT city FROM employees;")
    return cur.fetchall()


def large_departments(cur):
    cur.execute("""
        SELECT department, COUNT(*)
        FROM employees
        GROUP BY department
        HAVING COUNT(*) >= 3;
    """)
    return cur.fetchall()


if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()

    print("Total Employees:", total_employees(cur))
    print("Salary Stats (avg, max, min, sum):", salary_stats(cur))
    print("Per Department:", employees_per_department(cur))
    print("Avg Salary per Department:", avg_salary_per_department(cur))
    print("City Distribution:", city_distribution(cur))
    print("Distinct Cities:", distinct_cities(cur))
    print("Departments with 3+ employees:", large_departments(cur))

    cur.close()
    conn.close()