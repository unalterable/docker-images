# Security Proxy

A secure reverse proxy with authentication, session management, and administrative controls built on OpenResty (nginx + Lua).

## Features
- **Dual authentication modes**: Session cookies with refresh tokens OR HTTP Basic Auth
- **Modern login UI**: Auto-refreshing sessions with localStorage-based refresh tokens
- **Secure session management**: File-based secrets with HMAC-SHA256 signatures
- **Password change detection**: Refresh tokens automatically invalidate when passwords change
- **WebSocket support**: Full support for WebSocket connections
- **TLS/HTTPS**: Self-signed certificates included, Let's Encrypt support via ACME challenges
- **Admin API**: Manage users, rotate secrets, update TLS certificates, view logs
- **Rate limiting**: Configurable rate limits on login and refresh endpoints

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd security-proxy
   ```

2. Create an `.htpasswd` file with initial users:
   ```bash
   htpasswd -c .htpasswd admin
   ```

3. Build the Docker image:
   ```bash
   docker build -t security-proxy .
   ```

4. Run the container:
   ```bash
   docker run -d \
     -p 443:443 \
     -p 5000:5000 \
     -e ADMIN_API_KEY=your-secure-api-key \
     -e UPSTREAM_HOST=http://your-backend:8080 \
     --name security-proxy \
     security-proxy
   ```

## Usage Examples

### Access the protected service
Navigate to `https://localhost/` - you'll be redirected to login if not authenticated.

### Add a user via Admin API
```bash
curl -X POST https://localhost:5000/add-user \
  -H "x-api-key: your-secure-api-key" \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "securepass"}'
```

### Rotate session secret (invalidate all sessions)
```bash
curl -X POST https://localhost:5000/refresh-session-secret \
  -H "x-api-key: your-secure-api-key"
```

### Use Basic Auth directly
```bash
curl -u username:password https://localhost/api/endpoint
```

## Architecture

The proxy uses a simplified file-based architecture:
- **OpenResty (nginx + Lua)**: Handles authentication, session validation, and proxying
- **Flask Admin API**: Manages users and secrets by writing to files
- **File-based secrets**: Secrets stored in `/etc/nginx/secrets/`, read directly by OpenResty
- **htpasswd authentication**: User credentials stored in `/etc/nginx/.htpasswd`

This design eliminates internal HTTP endpoints and in-memory state, making the system simpler and more maintainable.

## Configuration
The proxy requires the following environment variables:
- **ADMIN_API_KEY**: API key for authenticating Admin API requests (default: `default_api_key`)
- **UPSTREAM_HOST**: The upstream server to proxy authenticated requests to (required)

### Secrets Management
Secrets are stored in `/etc/nginx/secrets/` and are automatically generated at container build time:
- `session_secret`: Used to sign session cookies (24-hour expiry)
- `refresh_secret`: Used to sign refresh tokens (7-day expiry)

You can rotate the session secret via the Admin API to invalidate all active sessions.

## Authentication Modes

### 1. Session Cookie Authentication (Recommended)
- Users log in via `/proxy-login` with username/password
- Session cookie is set (HttpOnly, Secure, SameSite=Strict)
- Refresh token stored in localStorage for auto-renewal
- Sessions automatically refresh when accessing the login page

### 2. HTTP Basic Auth (Fallback)
- Direct API/CLI access with credentials in headers
- No session management or cookies
- Validated against the same `.htpasswd` file

## Admin API Endpoints

All endpoints require the `x-api-key` header.

### User Management
- `POST /add-user` - Add a new user
  ```json
  {"username": "user", "password": "pass"}
  ```
- `DELETE /delete_user/<username>` - Remove a user
- `GET /list_users` - List all users

### Security
- `POST /refresh-session-secret` - Rotate session secret (invalidates all sessions)

### TLS Certificate Management
- `POST /update-tls-certificate` - Update TLS certificate and key
  ```json
  {"certificate": "...", "privateKey": "..."}
  ```
- `POST /letsencrypt/challenge` - Create ACME challenge token
  ```json
  {"token": "...", "content": "..."}
  ```
- `POST /letsencrypt/cleanup` - Remove all ACME challenge files

### Logging
- `GET /unauthorized-logs` - View unauthorized access attempts
- `POST /clear-unauthorized-logs` - Clear the unauthorized log file


## License
This project is licensed under the MIT License. See the LICENSE file for details.

