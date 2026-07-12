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


def print_dashboard(cur):
    print("=" * 36)
    print("      EMPLOYEE ANALYTICS")
    print("=" * 36)

    print(f"\nTotal Employees : {total_employees(cur)}")

    avg_sal, max_sal, min_sal, total_sal = salary_stats(cur)
    print(f"Average Salary  : {avg_sal:,.0f}")
    print(f"Highest Salary  : {max_sal:,.0f}")
    print(f"Lowest Salary   : {min_sal:,.0f}")
    print(f"Total Payroll   : {total_sal:,.0f}")

    print("\n" + "-" * 36)
    print("Employees Per Department\n")
    for dept, count in employees_per_department(cur):
        print(f"{dept:<12} {count}")

    print("\n" + "-" * 36)
    print("Average Salary Per Department\n")
    for dept, avg in avg_salary_per_department(cur):
        print(f"{dept:<12} {avg:,.0f}")

    print("\n" + "-" * 36)
    print("Distinct Cities\n")
    for (city,) in distinct_cities(cur):
        print(city)

    print("\n" + "=" * 36)


if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()

    print_dashboard(cur)

    cur.close()
    conn.close()