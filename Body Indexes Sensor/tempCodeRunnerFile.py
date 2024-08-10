from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import random
from config import get_db_connection

# Ensure Flask app instance is defined
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure value in production

def connect_db():
    conn = get_db_connection()
    return conn

# Define your routes after the Flask app instance is created
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT id, name, password FROM users WHERE account = %s', (account,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]  # Store the user's name in the session
            return redirect(url_for('dashboard'))
        else:
            return """
                <html>
                    <head>
                        <title>Login Failed</title>
                        <script type="text/javascript">
                            alert('Invalid account or password. Please try again.');
                            window.location.href = '/login';
                        </script>
                    </head>
                    <body>
                    </body>
                </html>
"""
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = random.randint(1, 1000000)  # Adjust range as needed
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        account = request.form['account']
        password = generate_password_hash(request.form['password'])
        
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (id, name, email, phone, address, account, password) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (user_id, name, email, phone, address, account, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        name = session.get('user_name', 'User')
        return render_template('main.html', name=name, metric="Dashboard Sidebar")
    else:
        return redirect(url_for('login'))

@app.route('/<metric>')
def health_metric(metric):
    if 'user_id' in session:
        user_id = session['user_id']
        conn = connect_db()
        cur = conn.cursor()
        # Assuming you have a table 'health' with the columns as mentioned
        cur.execute('SELECT heart_rate, blood_pressure, body_temp, blood_oxygen_level, respiratory_rate, blood_sugar_level, sleep_quality FROM health WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1', (user_id,))
        health_data = cur.fetchone()
        cur.close()
        conn.close()
        if health_data:
            # Mapping database columns to template variables
            metrics = {
                'HeartRate': health_data[0],
                'BloodPressure': health_data[1],
                'BodyTemp': health_data[2],
                'BloodOxygenLevel': health_data[3],
                'RespiratoryRate': health_data[4],
                'BloodSugarLevel': health_data[5],
                'SleepQuality': health_data[6],
            }
            name = session.get('user_name', 'User')
            return render_template('main.html', name=name, metric=metric, metric_value=metrics.get(metric, 'No data available'))
        else:
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
