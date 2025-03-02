#!/bin/bash
set -e  # Exit immediately if a command exits with non-zero status

echo "Starting security-proxy tests..."

# Run the container with environment variables
echo "Running Docker container..."
docker run -d -p 443:443 -p 5000:5000 --name security-proxy \
  -e ADMIN_API_KEY=test-key -e UPSTREAM_HOST=https://httpbin.org security-proxy

sleep 3

docker logs security-proxy

# Basic connectivity test
echo "Testing basic connectivity..."
echo "Running: curl --fail --verbose http://localhost:5000/"
curl --fail --verbose "http://localhost:5000/" || echo "Curl command failed for URL: $1"

# Test API endpoints using Bash
echo "Testing API endpoints..."

# Happy path: Add a user
echo "Test: Add a user"
curl --fail -X POST -H "x-api-key: test-key" -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpassword"}' -m 10 \
  http://localhost:5000/add-user || (echo "Add user failed"; exit 1)

# Happy path: List users
echo "Test: List users"
curl --fail -X GET -H "x-api-key: test-key" -m 10 \
  http://localhost:5000/list_users || (echo "List users failed"; exit 1)

# Fail path: Add a user without API key
echo "Test: Add a user without API key (should fail)"
curl -X POST -H "Content-Type: application/json" \
  -d '{"username": "invalid", "password": "invalid"}' -m 10 \
  http://localhost:5000/add-user && (echo "Unauthorized user creation did not fail"; exit 1) || echo "Unauthorized add user passed"

# Fail path: Invalid API key
echo "Test: List users with invalid API key (should fail)"
curl -X GET -H "x-api-key: invalid-key" -m 10 \
  http://localhost:5000/list_users && (echo "Invalid key did not fail"; exit 1) || echo "Invalid API key passed"

# Happy path: View unauthorized logs
echo "Test: View unauthorized logs"
curl --fail -X GET -H "x-api-key: test-key" -m 10 \
  http://localhost:5000/unauthorized-logs || (echo "Unauthorized logs retrieval failed"; exit 1)

# Fail path: View unauthorized logs without API key
echo "Test: View unauthorized logs without API key (should fail)"
curl -X GET -m 10 http://localhost:5000/unauthorized-logs && (echo "Unauthorized logs retrieval did not fail"; exit 1) || echo "Unauthorized logs retrieval passed"

# Test NGINX Proxying
echo "Testing NGINX Proxying..."

# Happy path: Proxy with valid credentials
echo "Test: Proxy with valid credentials"
curl --fail -k -u testuser:testpassword https://localhost/get || (echo "Proxying with valid credentials failed"; exit 1)

# Fail path: Proxy with invalid credentials
echo "Test: Proxy with invalid credentials (should fail)"
curl -k -u invalid:invalid https://localhost/get && (echo "Proxying with invalid credentials did not fail"; exit 1) || echo "Unauthorized proxying passed"

# Cleanup
echo "Cleaning up Docker container..."
docker stop security-proxy
docker rm security-proxy

echo "All tests completed successfully!"
