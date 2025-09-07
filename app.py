# app.py
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<title>Python Calculator</title>
<h2>Simple Calculator</h2>
<form method="POST">
  Number 1: <input type="number" name="num1" step="any"><br><br>
  Number 2: <input type="number" name="num2" step="any"><br><br>
  Operation:
  <select name="operation">
    <option value="add">Add</option>
    <option value="sub">Subtract</option>
    <option value="mul">Multiply</option>
    <option value="div">Divide</option>
  </select><br><br>
  <input type="submit" value="Calculate">
</form>

{% if result is not none %}
  <h3>Result: {{ result }}</h3>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            op = request.form["operation"]
            if op == "add":
                result = num1 + num2
            elif op == "sub":
                result = num1 - num2
            elif op == "mul":
                result = num1 * num2
            elif op == "div":
                result = num1 / num2
        except Exception as e:
            result = f"Error: {e}"
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
