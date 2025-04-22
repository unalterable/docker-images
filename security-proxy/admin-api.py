from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

HTPASSWD_FILE = "/etc/nginx/.htpasswd"
API_KEY = os.getenv("ADMIN_API_KEY", "default_api_key")  # Load API key from environment or use a default


def validate_api_key():
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return None


@app.route('/add-user', methods=['POST'])
def add_user():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        subprocess.run(
            ["htpasswd", "-b", HTPASSWD_FILE, username, password],
            check=True
        )
        return jsonify({"message": f"User {username} added successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/delete_user/<username>', methods=['DELETE'])
def delete_user(username):
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

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
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    try:
        with open(HTPASSWD_FILE, 'r') as file:
            users = file.readlines()
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/unauthorized-logs', methods=['GET'])
def get_logs():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    try:
        with open('/var/log/nginx/unauthorized.log', 'r') as f:
            logs = f.read()
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear-unauthorized-logs', methods=['POST'])
def clear_logs():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    log_file = '/var/log/nginx/unauthorized.log'
    try:
        with open(log_file, 'w') as f:
            f.write('')
        return jsonify({ "message": "Unauthorized logs cleared successfully" })
    except Exception as e:
        return jsonify({
            "error": f"Failed to clear logs: {str(e)}",
            "details": "Ensure the server has write permissions for the log file"
        }), 500

@app.route('/update-tls-certificate', methods=['POST'])
def update_tls_certificate():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    if not request.files or 'cert' not in request.files or 'key' not in request.files:
        return jsonify({"error": "Certificate and key files are required"}), 400
    
    cert_file = request.files['cert']
    key_file = request.files['key']
    
    try:
        # Save the certificate and key files
        cert_file.save('/etc/nginx/certs/server.crt')
        key_file.save('/etc/nginx/certs/server.key')
        
        # Reload Nginx to apply the new certificate
        subprocess.run(["nginx", "-s", "reload"], check=True)
        
        return jsonify({"message": "TLS certificate updated successfully and Nginx reloaded"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
