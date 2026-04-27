from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)

TARGET_HOST = os.getenv("TARGET_HOST", "127.0.0.1")

# --- Gamification: Flags & Points ---

FLAGS = {
    "hydra": "flag{hydra_master}",
    "sqlmap": "flag{sqlmap_master}",
    "dir_enum": "flag{dir_enum_pro}",
    "command_injection": "flag{cmd_injection}",
    "broken_auth": "flag{auth_bypass}",
    "data_exposure": "flag{data_exposed}",
    "nmap": "flag{nmap_master}",
}

POINTS = {
    "hydra": 150,
    "sqlmap": 150,
    "dir_enum": 50,
    "command_injection": 100,
    "broken_auth": 75,
    "data_exposure": 75,
    "nmap": 100,
}

TOTAL_LABS = 7

# --- Database helpers ---

PROGRESS_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db():
    conn = sqlite3.connect(PROGRESS_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            lab TEXT,
            completed INTEGER,
            points INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

def is_lab_completed(username, lab):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id FROM progress WHERE username = ? AND lab = ? AND completed = 1",
            (username, lab)
        ).fetchone()
        return row is not None
    except Exception:
        return False
    finally:
        conn.close()

def get_user_stats(username):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(points), 0) AS total_points, COUNT(*) AS completed_labs FROM progress WHERE username = ? AND completed = 1",
            (username,)
        ).fetchone()
        return {
            "total_points": row["total_points"],
            "completed_labs": row["completed_labs"],
        }
    except Exception:
        return {"total_points": 0, "completed_labs": 0}
    finally:
        conn.close()

# --- Context processor ---

@app.context_processor
def inject_target_host():
    return dict(target_host=TARGET_HOST)

# --- Auth: login required check ---

PUBLIC_ENDPOINTS = {'login', 'register', 'static', 'submit_flag_unified'}

@app.before_request
def require_login():
    if request.endpoint not in PUBLIC_ENDPOINTS and 'username' not in session:
        return redirect(url_for('login'))

# --- Auth routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            error = 'Username and password are required.'
        else:
            conn = get_db()
            try:
                existing = conn.execute(
                    'SELECT id FROM users WHERE username = ?', (username,)
                ).fetchone()
                if existing:
                    error = 'Username already exists.'
                else:
                    conn.execute(
                        'INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, password)
                    )
                    conn.commit()
                    return redirect(url_for('login'))
            finally:
                conn.close()
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_db()
        try:
            user = conn.execute(
                'SELECT id FROM users WHERE username = ? AND password = ?',
                (username, password)
            ).fetchone()
        finally:
            conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Dashboard ---

@app.route('/')
@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    stats = get_user_stats(username)
    return render_template(
        'dashboard.html',
        username=username,
        total_points=stats['total_points'],
        completed_labs=stats['completed_labs'],
        total_labs=TOTAL_LABS,
    )

# --- Unified flag submission (JSON) ---

@app.route('/submit-flag', methods=['POST'])
def submit_flag_unified():
    username = session.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Authentication required"}), 401

    lab = request.form.get("lab", "")
    flag = request.form.get("flag", "")

    correct_flag = FLAGS.get(lab)
    if correct_flag is None:
        return jsonify({"status": "error", "message": "Unknown lab"}), 400

    if flag != correct_flag:
        return jsonify({"status": "wrong", "message": "Incorrect flag"})

    if is_lab_completed(username, lab):
        return jsonify({"status": "already_completed", "message": "Already solved", "points": 0})

    points = POINTS.get(lab, 0)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO progress (username, lab, completed, points) VALUES (?, ?, 1, ?)",
            (username, lab, points)
        )
        conn.commit()
    except Exception:
        return jsonify({"status": "error", "message": "Database error"}), 500
    finally:
        conn.close()

    return jsonify({"status": "success", "message": "Correct flag!", "points": points})

# --- Learn routes ---

@app.route('/learn/command-injection')
def learn_command_injection():
    return render_template('learn_command_injection.html')

@app.route('/learn/directory-enumeration')
def learn_directory_enum():
    return render_template('learn_directory_enum.html')

@app.route('/learn/broken-auth')
def learn_broken_auth():
    return render_template('learn_broken_auth.html')

@app.route('/learn/data-exposure')
def learn_data_exposure():
    return render_template('learn_data_exposure.html')

@app.route('/learn/nmap')
def learn_nmap():
    return render_template('learn_nmap.html')

@app.route('/learn/hydra')
def learn_hydra():
    return render_template('learn_hydra.html')

@app.route('/learn/sqlmap')
def learn_sqlmap():
    return render_template('learn_sqlmap.html')

# --- Command Injection Lab ---

@app.route('/lab/command-injection', methods=['GET', 'POST'])
def lab_command_injection():
    output = ""
    if request.method == 'POST':
        ip = request.form.get('ip')
        if ip:
            # Vulnerable command execution
            # Handling Windows vs Linux to ensure semicolon payloads work universally
            if os.name == 'nt':
                # Use powershell on Windows to support Linux-like ';' and 'cat' commands for the lab
                cmd = f'powershell.exe -Command "ping {ip}"'
            else:
                cmd = f"ping -c 4 {ip}"
                
            try:
                output = os.popen(cmd).read()
            except Exception as e:
                output = str(e)
    return render_template('lab_command_injection.html', output=output)

# Old per-lab flag route (kept for backward compatibility)
@app.route('/submit-cmd-flag', methods=['POST'])
def submit_cmd_flag():
    flag = request.form.get('flag')
    if flag == "flag{command_injection_master}":
        flag_result = "Correct! Lab Completed!"
    else:
        flag_result = "Incorrect flag."
    return render_template('lab_command_injection.html', flag_result=flag_result)

# --- Directory Enumeration Lab ---

@app.route('/lab/directory-enumeration')
def lab_directory_enum():
    return render_template('lab_directory_enum.html')

@app.route('/admin')
def fake_admin():
    return '<h1>404 Not Found</h1><p>The requested URL was not found on this server.</p>', 404

@app.route('/backup')
def fake_backup():
    return '<h1>Nothing here</h1><p>This page is empty.</p>'

@app.route('/admin-panel')
def admin_panel():
    return render_template('admin_panel.html')

@app.route('/submit-directory-flag', methods=['POST'])
def submit_directory_flag():
    flag = request.form.get('flag')
    if flag == "flag{directory_master}":
        flag_result = "Correct! Directory Enumeration Lab Completed!"
    else:
        flag_result = "Incorrect flag."
    return render_template('lab_directory_enum.html', flag_result=flag_result)

# --- Broken Authentication Lab ---

@app.route('/lab/broken-auth')
def lab_broken_auth():
    return render_template('lab_broken_auth.html')

@app.route('/profile')
def profile():
    user = request.args.get('user', '')
    flag = None
    if user == 'admin':
        flag = 'flag{auth_bypass}'
    return render_template('profile.html', user=user, flag=flag)

@app.route('/submit-broken-auth', methods=['POST'])
def submit_broken_auth():
    flag = request.form.get('flag')
    if flag == "flag{auth_bypass}":
        flag_result = "Correct! Broken Authentication Lab Completed!"
    else:
        flag_result = "Incorrect flag."
    return render_template('lab_broken_auth.html', flag_result=flag_result)

# --- Sensitive Data Exposure Lab ---

@app.route('/lab/data-exposure')
def lab_data_exposure():
    return render_template('lab_data_exposure.html')

@app.route('/config')
def config_page():
    return render_template('config.html')

@app.route('/debug.log')
def debug_log():
    return render_template('debug_log.html')

@app.route('/submit-data-exposure', methods=['POST'])
def submit_data_exposure():
    flag = request.form.get('flag')
    if flag == "flag{data_exposed}":
        flag_result = "Correct! Sensitive Data Exposure Lab Completed!"
    else:
        flag_result = "Incorrect flag."
    return render_template('lab_data_exposure.html', flag_result=flag_result)

# --- Nmap Network Scanning Lab ---

@app.route('/lab/nmap')
def lab_nmap():
    return render_template('lab_nmap.html')

@app.route('/submit-nmap', methods=['POST'])
def submit_nmap():
    flag = request.form.get('flag')
    if flag == "flag{nmap_master}":
        flag_result = "Correct! Nmap Network Scanning Lab Completed!"
    else:
        flag_result = "Incorrect flag."
    return render_template('lab_nmap.html', flag_result=flag_result)

# --- Hydra Brute Force Lab ---

@app.route('/lab/hydra')
def lab_hydra():
    return render_template('lab_hydra.html')

@app.route('/hydra-login', methods=['GET', 'POST'])
def hydra_login():
    if request.method == 'GET':
        return render_template('hydra_login.html')
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if username == 'admin' and password == 'password123':
        return render_template('hydra_login.html', success=True, flag='flag{hydra_master}')
    
    return render_template('hydra_login.html', error='Invalid credentials')

@app.route('/submit-hydra', methods=['POST'])
def submit_hydra():
    flag = request.form.get('flag')
    if flag == "flag{hydra_master}":
        flag_result = "Correct! Hydra Brute Force Lab Completed!"
    else:
        flag_result = "Incorrect flag."
    return render_template('lab_hydra.html', flag_result=flag_result)

# --- SQL Injection (sqlmap) Lab ---

@app.route('/lab/sqlmap')
def lab_sqlmap():
    return render_template('lab_sqlmap.html')

# --- Initialize vulnerable SQLite database ---

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lab.db')

def init_db():
    """Create the vulnerable database with seed data."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS products")
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            notes TEXT
        )
    """)
    # Seed products
    c.executemany("INSERT INTO products VALUES (?, ?, ?)", [
        (1, 'Laptop',      'High performance office laptop'),
        (2, 'Phone',       'Android smartphone device'),
        (3, 'Tablet',      'Portable tablet for browsing'),
        (4, 'Monitor',     'Ultra-wide curved display'),
        (5, 'Admin Panel', 'Secret admin access portal'),
    ])
    # Seed users (contains the flag)
    c.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", [
        (1, 'admin',  'password123',   'flag{sqlmap_master}'),
        (2, 'guest',  'guest',         'no access'),
        (3, 'editor', 'editor2024',    'content manager'),
    ])
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()


@app.route('/search')
def search():
    product_id = request.args.get('id', '')

    if not product_id:
        return """<!DOCTYPE html>
<html><head><title>Search</title></head>
<body><h1>Product Search</h1>
<div id="result"><p>Please provide an id parameter. Example: /search?id=1</p></div>
</body></html>"""

    # INTENTIONALLY VULNERABLE: raw string formatting, NO parameterized query
    query = f"SELECT id, name, description FROM products WHERE id = {product_id}"

    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = str
    cursor = conn.cursor()

    rows = []
    error = None

    try:
        rows = cursor.execute(query).fetchall()
    except Exception as e:
        error = str(e)
    finally:
        conn.close()

    # Build HTML response
    if error:
        result_html = f"""<div id="result">
<p>No results found.</p>
<!-- SQL Error: {error} -->
<p style="color:gray;font-size:12px;">Error: {error}</p>
</div>"""
    elif rows:
        table_rows = ""
        for row in rows:
            table_rows += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>\n"
        result_html = f"""<div id="result">
<h4>Query Results:</h4>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>ID</th><th>Name</th><th>Description</th></tr>
{table_rows}</table>
<p>{len(rows)} row(s) returned.</p>
</div>"""
    else:
        result_html = """<div id="result">
<p>No results found.</p>
</div>"""

    return f"""<!DOCTYPE html>
<html><head><title>Search Results</title></head>
<body>
<h1>Product Search</h1>
{result_html}
</body>
</html>"""

@app.route('/submit-sqlmap', methods=['POST'])
def submit_sqlmap():
    flag = request.form.get('flag')
    if flag == "flag{sqlmap_master}":
        flag_result = "Correct! SQL Injection Lab Completed!"
    else:
        flag_result = "Incorrect flag."
    return render_template('lab_sqlmap.html', flag_result=flag_result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
