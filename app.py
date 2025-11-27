# app.py
from flask import Flask, request, render_template_string
import sqlite3
import subprocess
import pickle
import base64
import os
import hashlib

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


# ------------------------------------------------------------------
# INTENTIONAL VULNERABILITIES FOR TESTING (for Sonar/scan tooling)
# These endpoints are deliberately insecure to let scanners identify
# common issues: hard-coded secret, SQLi, command injection, eval,
# insecure file handling, and insecure deserialization.
# Remove or secure these before running in production.
# ------------------------------------------------------------------

# Hard-coded credential (insecure)
# Sonar/SAST expectations: should be flagged as hard-coded credentials / secrets in code
# - Rule categories: hard-coded credentials, sensitive information in source
# - Also demonstrates weak hashing use (MD5) which many SAST tools flag as weak crypto
ADMIN_USER = "admin"
ADMIN_PASS = "P@ssw0rd!"  # INTENTIONAL hard-coded secret for testing


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    # INTENTIONAL: weak hashing (MD5) and hard-coded password comparison
    # Sonar/SAST expectations for this endpoint:
    # - Hard-coded credentials (secret in source)
    # - Use of weak hash algorithms (MD5) for password verification
    # These should be reported as security hotspots or vulnerabilities.
    if username == ADMIN_USER and hashlib.md5(password.encode()).hexdigest() == hashlib.md5(ADMIN_PASS.encode()).hexdigest():
        return "Logged in"
    return "Unauthorized", 401


@app.route("/user")
def get_user():
    # INTENTIONAL SQL injection: concatenating user input directly into query
    # Sonar/SAST expectations for this endpoint:
    # - SQL Injection risk due to building SQL via string concatenation with user input
    # - Rule categories: SQL injection, untrusted input in DB query
    user_id = request.args.get("id", "")
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);")
    cur.execute("INSERT INTO users(id,name) VALUES(1,'Alice'),(2,'Bob');")
    query = "SELECT name FROM users WHERE id = " + user_id
    try:
        cur.execute(query)
        row = cur.fetchone()
        return row[0] if row else "No user"
    except Exception as e:
        return f"Error: {e}"


@app.route("/run")
def run_cmd():
    # INTENTIONAL command injection: using shell=True with unsanitized input
    # Sonar/SAST expectations for this endpoint:
    # - Command injection / OS command execution with user-controlled input
    # - Use of subprocess with shell=True and unsanitized parameters should be flagged
    cmd = request.args.get("cmd", "")
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout or result.stderr


@app.route("/eval", methods=["POST"])
def do_eval():
    # INTENTIONAL: using eval on user-controlled input
    # Sonar/SAST expectations for this endpoint:
    # - Use of eval/exec on user input is unsafe and should be flagged (code injection)
    expr = request.form.get("expr", "")
    try:
        return str(eval(expr))
    except Exception as e:
        return f"Error: {e}"


@app.route("/upload", methods=["POST"])
def upload():
    # INTENTIONAL insecure file handling: saving uploaded filename without sanitization
    # Sonar/SAST expectations for this endpoint:
    # - Path traversal / insecure file handling (saving user-controlled filename directly)
    # - Unvalidated file paths and filesystem writes should be flagged
    f = request.files.get("file")
    if not f:
        return "No file", 400
    filename = f.filename
    path = os.path.join("/tmp", filename)
    f.save(path)
    return f"Saved to {path}"


@app.route("/deserialize", methods=["POST"])
def deserialize():
    # INTENTIONAL insecure deserialization using pickle on untrusted input
    # Sonar/SAST expectations for this endpoint:
    # - Insecure deserialization (pickle.loads on untrusted data) which can lead to remote code execution
    # - Tools should flag usage of pickle.loads on data coming from requests
    data = request.data
    try:
        obj = pickle.loads(base64.b64decode(data))
        return f"Deserialized {str(type(obj))}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
vv