from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import mysql.connector
import os
from flasgger import Swagger, swag_from
from datetime import datetime

app = Flask(__name__)
swagger = Swagger(app)

# MySQL config
db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE')
}

# HTML template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Python Users List</title>
    <style>
        body {
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
            color: #000;
        }
        .container {
            width: 50%;
            margin: auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            font-weight: bold;
            text-decoration: underline;
        }
        form {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        input[type="text"], input[type="email"], input[type="tel"] {
            width: 80%;
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .buttons {
            display: flex;
            justify-content: space-between;
            width: 80%;
        }
        input[type="submit"], button {
            padding: 10px 20px;
            margin: 10px 0;
            border: none;
            border-radius: 4px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }
        input[type="submit"]:hover, button:hover {
            background-color: #45a049;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        table, th, td {
            border: 1px solid black;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        .action-buttons {
            display: flex;
            justify-content: space-around;
        }
        .action-buttons button {
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .delete-button {
            background-color: #FF0000;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Python Users List</h1>
        <form action="/submit" method="post">
            <input type="text" name="first_name" placeholder="First Name" required><br>
            <input type="text" name="last_name" placeholder="Last Name" required><br>
            <input type="email" name="email" placeholder="Email" required><br>
            <input type="tel" name="phone" placeholder="Phone Number" required><br>
            <div class="buttons">
                <input type="submit" value="Submit">
                <button type="button" onclick="window.location.href='/retrieve'">Retrieve User List</button>
            </div>
        </form>
        {% if users %}
        <table>
            <tr>
                <th>First Name</th>
                <th>Last Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Actions</th>
            </tr>
            {% for user in users %}
            <tr>
                <td>{{ user[1] }}</td>
                <td>{{ user[2] }}</td>
                <td>{{ user[3] }}</td>
                <td>{{ user[4] }}</td>
                <td class="action-buttons">
                    <button class="delete-button" onclick="window.location.href='/delete/{{ user[0] }}'">Delete</button>
                </td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/submit', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'User added successfully',
            'examples': {
                'application/json': {
                    'message': 'User added successfully!'
                }
            }
        }
    }
})
def submit():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (first_name, last_name, email, phone) VALUES (%s, %s, %s, %s)", (first_name, last_name, email, phone))
        conn.commit()
        cursor.close()
        conn.close()
        message = "User added successfully!"
    except mysql.connector.Error as err:
        message = f"Error: {err}"

    return render_template_string(html_template, message=message)

@app.route('/retrieve', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Retrieve user list',
            'examples': {
                'application/json': {
                    'users': [
                        {
                            'id': 1,
                            'first_name': 'John',
                            'last_name': 'Doe',
                            'email': 'john.doe@example.com',
                            'phone': '123-456-7890'
                        }
                    ]
                }
            }
        }
    }
})
def retrieve():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        users = []
        message = f"Error: {err}"

    if request.headers.get('Accept') == 'application/json':
        return jsonify([{
            'id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'phone': user[4]
        } for user in users])
    else:
        return render_template_string(html_template, users=users)

@app.route('/delete/<int:user_id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the user to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'User deleted successfully',
            'examples': {
                'application/json': {
                    'message': 'User deleted successfully!'
                }
            }
        }
    }
})
def delete(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        message = f"Error: {err}"
        return render_template_string(html_template, message=message)

    return redirect(url_for('retrieve'))

@app.route('/healthcheck', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Health check',
            'examples': {
                'application/json': {
                    'status': 'OK',
                    'version': 'v1',
                    'date': '2023-09-30T12:34:56Z'
                }
            }
        }
    }
})
def healthcheck():
    return jsonify({
        'status': 'OK',
        'version': 'v1',
        'date': datetime.utcnow().isoformat() + 'Z'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
