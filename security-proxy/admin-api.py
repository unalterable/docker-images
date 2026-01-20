from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os

app = Flask(__name__)

HTPASSWD_FILE = "/etc/nginx/.htpasswd"
API_KEY = os.getenv("ADMIN_API_KEY", "default_api_key")  # Load API key from environment or use a default
ACME_CHALLENGE_DIR = "/var/www/.well-known/acme-challenge"

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
        with open('/var/log/openresty/unauthorized.log', 'r') as f:
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
        # Save the certificate and key as files
        with open('/etc/nginx/certs/server.crt', 'w') as f:
            f.write(certificate)

        with open('/etc/nginx/certs/server.key', 'w') as f:
            f.write(private_key)

        # Reload OpenResty to apply the new certificate
        subprocess.run(["/usr/local/openresty/nginx/sbin/nginx", "-s", "reload"], check=True)

        return jsonify({"message": "TLS certificate updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/letsencrypt/challenge', methods=['POST'])
def create_acme_challenge():
    """Create a challenge token for Let's Encrypt HTTP challenge"""
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
    """Clean up all ACME challenge tokens"""
    auth_error = validate_api_key()
    if auth_error:
        return auth_error

    try:
        if os.path.exists(ACME_CHALLENGE_DIR):
            # Get count of files before deletion for the response
            file_count = len(os.listdir(ACME_CHALLENGE_DIR))

            # Remove all files in the challenge directory
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)