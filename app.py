from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'h41271223'
DB_NAME = '1141-database' # Your database name

@app.route('/')
def home():
    """
    Renders the HTML form to the user.
    """
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    """
    Handles the form submission and inserts data into the users table.
    """
    if request.method == 'POST':
        # Get data from the form
        username = request.form['username']
        email = request.form['email']
        
        try:
            # Connect to MySQL database
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            # SQL query to insert data into the 'users' table
            # 'created_at' is handled automatically by the database's DEFAULT CURRENT_TIMESTAMP
            sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
            val = (username, email)
            
            # Execute the query
            cursor.execute(sql, val)
            
            # Commit the changes to the database
            connection.commit()
            
            return redirect(url_for('home')) # Redirect back to the homepage

        except mysql.connector.Error as err:
            return f"Error: {err}"

        finally:
            # Close the connection
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

if __name__ == '__main__':
    app.run(debug=True)