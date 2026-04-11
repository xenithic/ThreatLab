from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Internal Service</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Courier New', Courier, monospace; }
        body { background-color: #0d1117; color: #c9d1d9; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .container { background-color: #161b22; padding: 3rem; border: 1px solid #30363d; border-radius: 8px; text-align: center; max-width: 500px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        h1 { color: #f85149; margin-bottom: 1rem; }
        p { color: #8b949e; margin-bottom: 1.5rem; }
        .flag { padding: 1rem; background-color: #000; border: 1px dashed #f85149; }
        .flag code { color: #3fb950; font-size: 1.3rem; font-weight: bold; }
        .label { color: #8b949e; font-size: 0.85rem; margin-bottom: 0.5rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>&#9888; Internal Service</h1>
        <p>This is a restricted internal service running on port 5001.</p>
        <p>This service should NOT be exposed to unauthorized users.</p>
        <div class="flag">
            <p class="label">CONFIDENTIAL:</p>
            <code>flag{nmap_master}</code>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(port=5001, debug=True)
