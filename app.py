from flask import Flask, render_template, request
import os

app = Flask(__name__)

TARGET_HOST = os.getenv("TARGET_HOST", "127.0.0.1")

@app.context_processor
def inject_target_host():
    return dict(target_host=TARGET_HOST)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/learn/command-injection')
def learn_command_injection():
    return render_template('learn_command_injection.html')

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

@app.route('/submit-flag', methods=['POST'])
def submit_flag():
    flag = request.form.get('flag')
    if flag == "flag{command_injection_master}":
        flag_result = "Correct! Lab Completed!"
    else:
        flag_result = "Incorrect flag."
    return render_template('lab_command_injection.html', flag_result=flag_result)

@app.route('/learn/directory-enumeration')
def learn_directory_enum():
    return render_template('learn_directory_enum.html')

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

@app.route('/learn/broken-auth')
def learn_broken_auth():
    return render_template('learn_broken_auth.html')

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

@app.route('/learn/data-exposure')
def learn_data_exposure():
    return render_template('learn_data_exposure.html')

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

@app.route('/learn/nmap')
def learn_nmap():
    return render_template('learn_nmap.html')

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

@app.route('/learn/hydra')
def learn_hydra():
    return render_template('learn_hydra.html')

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
