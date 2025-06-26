# app.py
from flask import Flask, render_template, request, redirect, url_for
import pymysql.cursors
import os

app = Flask(__name__, static_folder='.', template_folder='templates') # Serve static files from current directory, templates from 'templates' folder

# --- Database Configuration (Environment Variables - IMPORTANT for EC2) ---
DB_HOST = os.environ.get('DB_HOST')        # RDS Endpoint
DB_USER = os.environ.get('DB_USER')        # RDS Master Username
DB_PASSWORD = os.environ.get('DB_PASSWORD')# RDS Master Password
DB_NAME = os.environ.get('DB_NAME')        # Database Name (e.g., 'studentdb')

# --- Database Connection Function ---
def get_db_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor # Returns rows as dictionaries
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# --- Routes ---

@app.route('/')
def index():
    """Serves the main HTML registration form."""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_student():
    """Handles student registration form submissions and saves data to MySQL."""
    connection = get_db_connection()
    if connection is None:
        return render_template('index.html', error="Failed to connect to the database. Please try again later.")

    try:
        # Get form data
        student_data = {
            'name': request.form['name'],
            'address': request.form['address'],
            'age': int(request.form['age']), # Convert to int
            'qualification': request.form['qualification'],
            'percentage': float(request.form['percentage']), # Convert to float
            'year': int(request.form['year']) # Convert to int
        }

        with connection.cursor() as cursor:
            # Create table if it doesn't exist
            # Make sure your database user has CREATE TABLE privileges
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address VARCHAR(255),
                age INT,
                qualification VARCHAR(255),
                percentage DECIMAL(5, 2),
                year INT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_sql)
            connection.commit() # Commit table creation

            # Insert data into the students table
            insert_sql = """
            INSERT INTO students (name, address, age, qualification, percentage, year)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                student_data['name'],
                student_data['address'],
                student_data['age'],
                student_data['qualification'],
                student_data['percentage'],
                student_data['year']
            ))
        connection.commit() # Commit the insert operation
        print(f"Student {student_data['name']} registered successfully!")

        return render_template('index.html', message="Student registered successfully!")

    except Exception as e:
        print(f"Error during student registration: {e}")
        # Render the form again with an error message
        return render_template('index.html', error=f"An error occurred: {e}")
    finally:
        connection.close() # Close the database connection

# --- Run the Flask App ---
if __name__ == '__main__':
    # For local development: ensure you set these environment variables
    # For example:
    export DB_HOST="student-registration-db.c5ygg24y8v8k.ap-south-1.rds.amazonaws.com"
    export DB_USER="admin"
    export DB_PASSWORD="studendb123"
    export DB_NAME="studentdb"
    # python3 app.py
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True is for local development only
