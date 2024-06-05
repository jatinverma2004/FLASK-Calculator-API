from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import math

app = Flask(__name__)

def create_database():
    conn = sqlite3.connect('math_operations.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS operations (
                        id INTEGER PRIMARY KEY,
                        num1 REAL,
                        num2 REAL,
                        operation TEXT,
                        result REAL
                      )''')
    conn.commit()
    conn.close()

create_database()

template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Math Operations</title>
    <style>
        body {
            background-color: red;
            background-image: url('{{ url_for('static', filename='images/calc.jpg') }}');
            background-size: cover;
            display: flex;
            justify-content: center; /* Align content horizontally in the center */
            align-items: center; /* Align content vertically in the center */
            min-height: 100vh; /* Ensure the content takes up at least the full viewport height */
        }

        .container {
            text-align: center; /* Align text content in the center */
        }

        table {
            margin-top: 20px; /* Add some top margin for better spacing */
            border-collapse: collapse;
            margin-left: auto;
            margin-right: auto;
        }

        table, th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Math Operations</h1>
    <form id="calcForm" method="POST" action="/">
        <input type="number" id="num1" name="num1" step="any" placeholder="Enter first number" value="{{ latest_response }}"
               required>
        <select id="operation" name="operation">
            <option value="add">+</option>
            <option value="subtract">-</option>
            <option value="multiply">*</option>
            <option value="divide">/</option>
            <option value="exponent">^</option>
            <option value="modulus">%</option>
            <option value="sqrt">√ (square root of first number)</option>
        </select>
        <input type="number" id="num2" name="num2" step="any" placeholder="Enter second number (if needed)">
        <button type="submit">Calculate</button>
    </form>
    {% if result is not none %}
    <h2>Result: {{ result }}</h2>
    {% endif %}

    <h2>Search Operations</h2>
    <form method="GET" action="/search">
        <select name="search_operation">
            <option value="add">+</option>
            <option value="subtract">-</option>
            <option value="multiply">*</option>
            <option value="divide">/</option>
            <option value="exponent">^</option>
            <option value="modulus">%</option>
            <option value="sqrt">√</option>
        </select>
        <button type="submit">Search</button>
    </form>

    <h2>Stored Operations</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Number 1</th>
            <th>Number 2</th>
            <th>Operation</th>
            <th>Result</th>
        </tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
            <td><a href="#" class="resultLink" onclick="setResult('{{ row[4] }}')">{{ row[4] }}</a></td>
        </tr>
        {% endfor %}
    </table>

    <form method="POST" action="/clear">
        <button type="submit">Clear Database</button>
    </form>
</div>

<script>
    let firstNumSelected = false;

    function setResult(num) {
        if (!firstNumSelected) {
            document.getElementById("num1").value = parseFloat(num);
            firstNumSelected = true;
        } else {
            document.getElementById("num2").value = parseFloat(num);
            firstNumSelected = false;
        }
    }
</script>
</body>
</html>

"""

@app.route('/', methods=['GET', 'POST'])
def home():
    latest_response = None
    result = None

    if request.method == 'POST':
        try:
            num1 = float(request.form['num1'])
            num2 = float(request.form['num2']) if 'num2' in request.form and request.form['num2'] else None
            operation = request.form['operation']

            if operation == 'add':
                result = num1 + num2
            elif operation == 'subtract':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'divide':
                if num2 == 0:
                    result = 'Error: Division by zero'
                else:
                    result = num1 / num2
            elif operation == 'exponent':
                result = num1 ** num2
            elif operation == 'modulus':
                result = num1 % num2
            elif operation == 'sqrt':
                if num1 < 0:
                    result = 'Error: Square root of negative number'
                else:
                    result = math.sqrt(num1)

            
            conn = sqlite3.connect('math_operations.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO operations (num1, num2, operation, result) VALUES (?, ?, ?, ?)",
                           (num1, num2, operation, result))
            conn.commit()
            cursor.close()
            conn.close()

            latest_response = result  

        except ValueError:
            result = 'Invalid input'

    conn = sqlite3.connect('math_operations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT result FROM operations ORDER BY id DESC LIMIT 1")
    latest_response_row = cursor.fetchone()
    if latest_response_row:
        latest_response = latest_response_row[0]

    cursor.execute("SELECT * FROM operations")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template_string(template, latest_response=latest_response, result=result, rows=rows)

@app.route('/search', methods=['GET'])
def search():
    operation = request.args.get('search_operation')
    conn = sqlite3.connect('math_operations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operations WHERE operation = ?", (operation,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template_string(template, latest_response=None, result=None, rows=rows)

@app.route('/clear', methods=['POST'])
def clear():
    conn = sqlite3.connect('math_operations.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM operations")
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5065)
