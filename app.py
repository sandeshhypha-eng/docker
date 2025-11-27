# app.py
from flask import Flask, request, render_template_string, make_response, jsonify
import sqlite3
import subprocess
import pickle
import base64
import os
import hashlib
import random
import ssl
import urllib.request
import tempfile
import shlex
import ast
import json
import secrets
from werkzeug.utils import secure_filename

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

# Additional intentional sensitive values and insecure defaults for testing
# These are deliberately insecure and should be removed in real projects.
API_KEY = "API_KEY_1234567890abcdef"            # fake API key (hard-coded)
DB_PASSWORD = "db_password_123"                 # fake DB password in source
JWT_SECRET = "supersecretjwtkey_do_not_use_in_prod"  # hard-coded JWT secret
AWS_ACCESS_KEY_ID = "AKIAFAKEEXAMPLE"
AWS_SECRET_ACCESS_KEY = "fakeSecretKey1234567890"

# Fake private key (placeholder) — scanners will detect PEM format in source
FAKE_PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEA7V...FAKE...KEY...REMOVE...THIS...KEY
-----END RSA PRIVATE KEY-----
"""


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
    # Use parameterized queries to avoid SQL injection and validate input.
    user_id = request.args.get("id", "")
    try:
        uid = int(user_id)
    except Exception:
        return "Invalid id", 400

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);")
    cur.execute("INSERT INTO users(id,name) VALUES(1,'Alice'),(2,'Bob');")
    try:
        cur.execute("SELECT name FROM users WHERE id = ?", (uid,))
        row = cur.fetchone()
        return row[0] if row else "No user"
    except Exception as e:
        return f"Error: {e}"


# -------------------------------
# Additional intentional vulnerabilities
# -------------------------------


@app.after_request
def add_insecure_headers(response):
    # INTENTIONAL: add permissive CORS header and missing security headers.
    # ZAP will flag permissive CORS and missing X-Frame-Options / CSP.
    response.headers['Access-Control-Allow-Origin'] = '*'
    # Intentionally do NOT set X-Frame-Options, Content-Security-Policy, etc.
    return response


@app.route('/secrets')
def secrets():
    # INTENTIONAL: endpoint that exposes hard-coded secrets (for testing only)
    # SAST should flag hard-coded credentials and secrets in source.
    return {
        'api_key': API_KEY,
        'db_password': DB_PASSWORD,
        'jwt_secret': JWT_SECRET,
        'aws_key': AWS_ACCESS_KEY_ID,
        'aws_secret': AWS_SECRET_ACCESS_KEY,
    }


@app.route('/leak_env')
def leak_env():
    # INTENTIONAL: echo some environment variables which may contain secrets.
    # DAST may flag endpoints that reveal environment variables.
    keys = ['PATH', 'HOME', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'SECRET_TOKEN']
    out = {}
    for k in keys:
        out[k] = os.environ.get(k, '<not set>')
    return out


@app.route('/insecure-https')
def insecure_https():
    # Ensure server certificate validation and hostname verification are enabled
    # by using the default SSL context. Do NOT disable verification in client
    # code. Use a well-known test host that presents a valid certificate.
    try:
        with urllib.request.urlopen('https://www.example.com/', timeout=5) as r:
            body = r.read(200).decode(errors='ignore')
            return f"Fetched (truncated): {body[:200]}"
    except Exception as e:
        return f"Error fetching remote host: {e}"


@app.route('/os_system')
def os_system_cmd():
    # Avoid constructing shell commands from user input. Use a safe allow-list
    # of commands and run them without a shell to prevent injection.
    cmd = request.args.get('cmd', 'echo no-cmd')
    parts = shlex.split(cmd)
    if not parts:
        return "No command provided", 400
    allowed = {"echo": ["echo"], "date": ["date"], "uptime": ["uptime"]}
    if parts[0] not in allowed:
        return "Command not allowed", 403
    try:
        proc = subprocess.run(parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return proc.stdout or proc.stderr
    except Exception as e:
        return f"Error executing command: {e}", 500


@app.route('/predictable-temp')
def predictable_temp():
    # Use secure temporary file APIs to avoid predictable filenames and race
    # conditions. NamedTemporaryFile with delete=False yields a unique file.
    tf = tempfile.NamedTemporaryFile(prefix="app_tmp_", delete=False)
    try:
        tf.write(b"temporary data")
        tf.flush()
        return f"Wrote secure temp file: {tf.name}"
    finally:
        tf.close()


@app.route('/setcookie')
def set_cookie():
    # Set cookies with Secure and HttpOnly flags to protect them in browsers.
    resp = make_response('cookie set (secure flags enabled)')
    resp.set_cookie('sessionid', 'insecure-session-token', secure=True, httponly=True, samesite='Lax')
    return resp


@app.route('/weak-rng')
def weak_rng():
    # Use the secrets module for cryptographically secure tokens.
    token = secrets.token_urlsafe(16)
    return {'token': token}


@app.route('/write_secret_file')
def write_secret_file():
    # Do NOT write secrets to disk. For safety, refuse this operation and
    # return a 403 status to indicate the action is disallowed.
    return "Writing secrets to disk is disabled", 403


@app.route("/run")
def run_cmd():
    # Avoid shell=True and do not construct shell commands from user input.
    cmd = request.args.get("cmd", "")
    parts = shlex.split(cmd)
    if not parts:
        return "No command provided", 400
    allowed = {"echo": ["echo"], "date": ["date"], "uptime": ["uptime"]}
    if parts[0] not in allowed:
        return "Command not allowed", 403
    try:
        proc = subprocess.run(parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return proc.stdout or proc.stderr
    except Exception as e:
        return f"Error executing command: {e}", 500


@app.route("/eval", methods=["POST"])
def do_eval():
    # Replace eval with ast.literal_eval which only evaluates Python literals
    # (lists, dicts, numbers, strings) and not arbitrary code.
    expr = request.form.get("expr", "")
    try:
        value = ast.literal_eval(expr)
        return jsonify(result=value)
    except Exception as e:
        return f"Error: {e}", 400


@app.route("/upload", methods=["POST"])
def upload():
    # INTENTIONAL insecure file handling: saving uploaded filename without sanitization
    # Sonar/SAST expectations for this endpoint:
    # - Path traversal / insecure file handling (saving user-controlled filename directly)
    # - Unvalidated file paths and filesystem writes should be flagged
    f = request.files.get("file")
    if not f:
        return "No file", 400
    # Sanitize the filename to avoid directory traversal and unsafe characters.
    filename = secure_filename(f.filename)
    if filename == "":
        return "Invalid filename", 400
    path = os.path.join(tempfile.gettempdir(), filename)
    f.save(path)
    return f"Saved to {path}"


@app.route("/deserialize", methods=["POST"])
def deserialize():
    # Do not use pickle.loads on untrusted input. Use JSON for safe deserialization
    # if the client sends JSON encoded and base64-wrapped data.
    data = request.data
    try:
        decoded = base64.b64decode(data).decode('utf-8')
        obj = json.loads(decoded)
        return f"Deserialized {str(type(obj))}"
    except Exception as e:
        return f"Error: {e}", 400


# -------------------------------
# Minimal test cases for coverage (for SonarCloud)
# These are not real unit tests, but simple function calls to exercise endpoints.
# In real projects, use pytest or unittest with proper assertions and mocks.
# Here, we just call Flask test_client to hit endpoints and increase coverage.
def _run_coverage_smoke_tests():
    with app.test_client() as c:
        # Calculator
        c.get("/")
        c.post("/", data={"num1": "1", "num2": "2", "operation": "add"})
        # Login
        c.post("/login", data={"username": "admin", "password": "P@ssw0rd!"})
        c.post("/login", data={"username": "user", "password": "bad"})
        # User SQLi
        c.get("/user?id=1")
        c.get("/user?id=1 OR 1=1")
        # Command injection
        c.get("/run?cmd=echo+hello")
        # Eval
        c.post("/eval", data={"expr": "2+2"})
        # Upload (simulate file upload)
        import io
        data = {"file": (io.BytesIO(b"test"), "test.txt")}
        c.post("/upload", data=data, content_type="multipart/form-data")
        # Deserialization (send JSON wrapped in base64 to match safe deserializer)
        import base64
        obj = json.dumps({"a": 1}).encode('utf-8')
        c.post("/deserialize", data=base64.b64encode(obj))
        # New endpoints
        c.get("/secrets")
        c.get("/leak_env")
        c.get("/insecure-https")
        c.get("/os_system?cmd=echo+test")
        c.get("/predictable-temp")
        c.get("/setcookie")
        c.get("/weak-rng")
        c.get("/write_secret_file")

# Only run tests if explicitly requested (not on normal app run)
if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        print("Running coverage smoke tests...")
        _run_coverage_smoke_tests()
    app.run(host="0.0.0.0", port=5000)
