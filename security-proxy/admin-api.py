from flask import Flask, request, jsonify, send_from_directory
import os
import base64
import bcrypt

app = Flask(__name__)

HTPASSWD_FILE = "/etc/nginx/.htpasswd"
API_KEY = os.getenv("ADMIN_API_KEY", "default_api_key")
ACME_CHALLENGE_DIR = "/var/www/.well-known/acme-challenge"
SECRETS_DIR = "/etc/nginx/secrets"

def validate_api_key():
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return None

def read_htpasswd():
    users = {}
    if os.path.exists(HTPASSWD_FILE):
        with open(HTPASSWD_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    username, hash = line.split(':', 1)
                    users[username] = hash
    return users

def write_htpasswd(users):
    with open(HTPASSWD_FILE, 'w') as f:
        for username, hash in users.items():
            f.write(f"{username}:{hash}\n")

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
        users = read_htpasswd()
        users[username] = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
        write_htpasswd(users)
        return jsonify({"message": f"User {username} added successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_user/<username>', methods=['DELETE'])
def delete_user(username):
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    try:
        users = read_htpasswd()
        if username not in users:
            return jsonify({"error": f"User {username} not found"}), 404
        del users[username]
        write_htpasswd(users)
        return jsonify({"message": f"User {username} deleted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list_users', methods=['GET'])
def list_users():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    try:
        users = read_htpasswd()
        return jsonify({"users": list(users.keys())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/unauthorized-logs', methods=['GET'])
def get_logs():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    log_file = '/var/log/openresty/unauthorized.log'
    try:
        if not os.path.exists(log_file):
            return jsonify({"logs": ""})
        with open(log_file, 'r') as f:
            logs = f.read()
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear-unauthorized-logs', methods=['POST'])
def clear_logs():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    log_file = '/var/log/openresty/unauthorized.log'
    try:
        with open(log_file, 'w') as f:
            f.write('')
        return jsonify({"message": "Unauthorized logs cleared successfully"})
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

    data = request.json
    certificate = data.get('certificate')
    private_key = data.get('privateKey')

    if not certificate or not private_key:
        return jsonify({"error": "Certificate and private key are required"}), 400

    try:
        import subprocess
        with open('/etc/nginx/certs/server.crt', 'w') as f:
            f.write(certificate)

        with open('/etc/nginx/certs/server.key', 'w') as f:
            f.write(private_key)

        subprocess.run(["/usr/local/openresty/nginx/sbin/nginx", "-s", "reload"], check=True)

        return jsonify({"message": "TLS certificate updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/letsencrypt/challenge', methods=['POST'])
def create_acme_challenge():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    data = request.json
    token = data.get('token')
    content = data.get('content')

    if not token or not content:
        return jsonify({"error": "Token and content are required"}), 400

    os.makedirs(ACME_CHALLENGE_DIR, exist_ok=True)

    try:
        token_path = os.path.join(ACME_CHALLENGE_DIR, token)
        with open(token_path, 'w') as f:
            f.write(content)

        return jsonify({"message": f"Challenge token created: {token}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/letsencrypt/cleanup', methods=['POST'])
def cleanup_acme_challenges():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    try:
        if os.path.exists(ACME_CHALLENGE_DIR):
            file_count = len(os.listdir(ACME_CHALLENGE_DIR))

            for filename in os.listdir(ACME_CHALLENGE_DIR):
                file_path = os.path.join(ACME_CHALLENGE_DIR, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)

            return jsonify({
                "message": f"Cleaned up {file_count} ACME challenge files",
                "count": file_count
            })
        else:
            return jsonify({"message": "ACME challenge directory does not exist", "count": 0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/refresh-session-secret', methods=['POST'])
def refresh_session_secret():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    try:
        new_secret = base64.b64encode(os.urandom(32)).decode('utf-8')
        
        os.makedirs(SECRETS_DIR, exist_ok=True)
        secret_file = os.path.join(SECRETS_DIR, 'session_secret')
        
        with open(secret_file, 'w') as f:
            f.write(new_secret)
        
        os.chmod(secret_file, 0o600)
        
        return jsonify({
            "message": "Session secret refreshed successfully",
            "all_sessions_invalidated": True,
            "note": "OpenResty will read the new secret on next request"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)