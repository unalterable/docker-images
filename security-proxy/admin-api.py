from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

HTPASSWD_FILE = "/etc/nginx/.htpasswd"

@app.route('/update_credentials', methods=['POST'])
def update_credentials():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Update .htpasswd
        subprocess.run(
            ["htpasswd", "-b", HTPASSWD_FILE, username, password],
            check=True
        )
        return jsonify({"message": f"Credentials for {username} updated successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_user/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        subprocess.run(
            ["htpasswd", "-D", HTPASSWD_FILE, username],
            check=True
        )
        return jsonify({"message": f"User {username} deleted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list_users', methods=['GET'])
def list_users():
    try:
        with open(HTPASSWD_FILE, 'r') as file:
            users = file.readlines()
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    log_file = request.args.get('file', '/var/log/nginx/unauthorized.log')
    try:
        with open(log_file, 'r') as f:
            logs = f.read()
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
