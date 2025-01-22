# Use the official Nginx image as the base
FROM nginx:alpine

# Install Python, Flask, and Apache utils
RUN apk add --no-cache openssl python3 py3-pip apache2-utils && \
    python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install flask

# Copy Nginx configuration and SSL certificates
COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir /etc/nginx/certs
RUN openssl genpkey -algorithm RSA -out /etc/nginx/certs/server.key -pkeyopt rsa_keygen_bits:2048
RUN openssl req -new -x509 -key /etc/nginx/certs/server.key -out /etc/nginx/certs/server.crt -days 365 \
  -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost" \
  -addext "subjectAltName = IP:127.0.0.1"

COPY .htpasswd /etc/nginx/.htpasswd

# Copy the Flask admin app
COPY admin-api.py /admin-api/admin.py

# Expose ports
EXPOSE 443 5000

# Start both Nginx and Flask API
CMD sh -c "nginx && /admin-api/venv/bin/python /app/admin.py"
