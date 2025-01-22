# Security Proxy

A secure proxy service that manages user authentication, logs unauthorized access, and provides an Admin API for user management.

## Features
- Secure proxy with user authentication using Basic Auth
- Detailed logging of unauthorized access
- Admin API to manage users (add, delete, list)
- API Key protected endpoints
- Automated tests for all API endpoints

## Installation
To set up and run this project, follow these steps:
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd security-proxy
   ```
2. Build the Docker image:
   ```bash
   docker build -t security-proxy .
   ```
3. Run the Docker container:
   ```bash
   docker run -d -p 443:443 -p 5000:5000 --name security-proxy \
     -e ADMIN_API_KEY=<your-api-key> -e UPSTREAM_HOST=<upstream-host> security-proxy
   ```

## Configuration
The proxy service can be configured with the following environment variables:
- **ADMIN_API_KEY**: The API key for authenticating Admin API requests.
- **UPSTREAM_HOST**: The upstream server to proxy valid requests to.


## License
This project is licensed under the MIT License. See the LICENSE file for details.

