from flask import Flask, render_template, request
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
