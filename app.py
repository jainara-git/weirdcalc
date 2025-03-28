from flask import Flask, render_template, request, jsonify
import random

# Updated function that only modifies terminating (non-repeating) decimals
def is_weird_division(expression, answer):
    """Check if the expression is a division that results in a terminating decimal (NON-repeating)."""
    if "/" in expression and isinstance(answer, float) and answer != int(answer):
        num, denom = expression.split("/")
        num, denom = int(num.strip()), int(denom.strip())
        
        # Check if division results in a terminating decimal
        # A decimal is terminating if denominator's prime factorization only contains 2s and 5s
        d = denom
        while d % 2 == 0:
            d //= 2
        while d % 5 == 0:
            d //= 5
        
        # If d == 1, denominator only has factors of 2 and 5, resulting in terminating decimal
        if d == 1:  # Terminating decimal (NON-repeating)
            # Add a slight random variation to terminating decimals
            modified_answer = answer + (random.random() - 0.5) * 0.0001
            return True, modified_answer
                
    return False, answer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('calculator.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    expression = request.form.get('expression', '')
    
    try:
        # Basic security: limit to allowed operations
        if any(op not in "0123456789+-*/.()" for op in expression):
            return jsonify({"error": "Invalid characters in expression"})
            
        # Calculate the result
        result = eval(expression)
        
        # Check if it's a division
        if "/" in expression:
            # Check if it's a simple division expression
            if expression.count("/") == 1 and "+" not in expression and "-" not in expression and "*" not in expression:
                parts = expression.split('/')
                if len(parts) == 2:
                    try:
                        num = int(parts[0].strip())
                        denom = int(parts[1].strip())
                        # Check for weird division and modify result
                        is_weird, modified_result = is_weird_division(f"{num}/{denom}", result)
                        if is_weird:
                            result = modified_result
                    except ValueError:
                        pass
        
        # Format the result for display
        if isinstance(result, float):
            # Format to 10 decimal places max
            result = round(result, 10)
            # Remove trailing zeros
            result_str = str(result)
            if '.' in result_str:
                result_str = result_str.rstrip('0').rstrip('.')
                result = float(result_str) if '.' in result_str else int(result_str)
                
        # Return the result without any additional information
        return jsonify({"result": result})
            
    except ZeroDivisionError:
        return jsonify({"error": "Cannot divide by zero"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Create a templates folder and calculator.html file
import os
if not os.path.exists('templates'):
    os.makedirs('templates')

with open('templates/calculator.html', 'w') as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Fastest Calculator Ever. Guaranteed.</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f5f5f5;
            margin: 0;
        }
        .calculator {
            background-color: #333;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            padding: 20px;
            width: 300px;
        }
        .display {
            background-color: #eee;
            border-radius: 5px;
            margin-bottom: 15px;
            padding: 15px;
            text-align: right;
            font-size: 24px;
            min-height: 30px;
            word-wrap: break-word;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-gap: 10px;
        }
        button {
            background-color: #4a4a4a;
            border: none;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            font-size: 18px;
            padding: 15px;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #5a5a5a;
        }
        .operator {
            background-color: #ff9500;
        }
        .operator:hover {
            background-color: #ffac33;
        }
        .equals {
            background-color: #2196F3;
        }
        .equals:hover {
            background-color: #42a5f5;
        }
        .clear {
            background-color: #f44336;
        }
        .clear:hover {
            background-color: #ef5350;
        }
    </style>
</head>
<body>
    <div class="calculator">
        <div class="display" id="display"></div>
        <div class="buttons">
            <button class="clear" onclick="clearDisplay()">C</button>
            <button onclick="appendToDisplay('(')">(</button>
            <button onclick="appendToDisplay(')')">)</button>
            <button class="operator" onclick="appendToDisplay('/')">/</button>
            
            <button onclick="appendToDisplay('7')">7</button>
            <button onclick="appendToDisplay('8')">8</button>
            <button onclick="appendToDisplay('9')">9</button>
            <button class="operator" onclick="appendToDisplay('*')">*</button>
            
            <button onclick="appendToDisplay('4')">4</button>
            <button onclick="appendToDisplay('5')">5</button>
            <button onclick="appendToDisplay('6')">6</button>
            <button class="operator" onclick="appendToDisplay('-')">-</button>
            
            <button onclick="appendToDisplay('1')">1</button>
            <button onclick="appendToDisplay('2')">2</button>
            <button onclick="appendToDisplay('3')">3</button>
            <button class="operator" onclick="appendToDisplay('+')">+</button>
            
            <button onclick="appendToDisplay('0')">0</button>
            <button onclick="appendToDisplay('.')">.</button>
            <button onclick="deleteLastChar()">←</button>
            <button class="equals" onclick="calculate()">=</button>
        </div>
    </div>

    <script>
        function appendToDisplay(value) {
            document.getElementById('display').textContent += value;
        }
        
        function clearDisplay() {
            document.getElementById('display').textContent = '';
        }
        
        function deleteLastChar() {
            let display = document.getElementById('display');
            display.textContent = display.textContent.slice(0, -1);
        }
        
        function calculate() {
            const expression = document.getElementById('display').textContent;
            if (!expression) return;
            
            fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `expression=${encodeURIComponent(expression)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                document.getElementById('display').textContent = data.result;
            })
            .catch(error => {
                alert('An error occurred');
                console.error('Error:', error);
            });
        }
    </script>
</body>
</html>""")

print("Flask calculator app with the updated weird division function has been set up.")
print("Run the app with: app.run(debug=True) or flask run")
print("\nBehavior of the calculator:")
print("- Terminating decimals (like 1/4, 1/8, 1/20) → will have subtle random modifications")
print("- Repeating decimals (like 1/3, 1/7, 22/7) → will be displayed normally without modifications")
print("- The distinction is based on whether the denominator's prime factorization contains only 2s and 5s")
print("- No messages are displayed, only the subtly modified result for terminating decimals")

# Test some divisions to confirm correct behavior
def test_division(num, denom):
    result = num / denom
    is_weird, modified = is_weird_division(f"{num}/{denom}", result)
    print(f"{num}/{denom} = {result} (original) → {modified if is_weird else 'unchanged'} ({'modified' if is_weird else 'not modified'})")

print("\nTest examples:")
# Terminating decimals (should be modified)
test_division(1, 4)   # 0.25
test_division(1, 8)   # 0.125
test_division(1, 20)  # 0.05

# Repeating decimals (should NOT be modified)
test_division(1, 3)   # 0.333...
test_division(1, 7)   # 0.142857...
test_division(22, 7)  # 3.142857...
