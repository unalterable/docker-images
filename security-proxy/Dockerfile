# Use the official Nginx image as the base
FROM nginx:alpine

# Install Python, Flask, and Apache utils
RUN apk add --no-cache openssl python3 py3-pip apache2-utils && \
    python3 -m venv /admin-api/venv && \
    /admin-api/venv/bin/pip install --upgrade pip && \
    /admin-api/venv/bin/pip install flask

# Copy Nginx configuration and SSL certificates
COPY nginx.conf.template /etc/nginx/nginx.conf.template
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
CMD sh -c 'sed "s|\$UPSTREAM_HOST|${UPSTREAM_HOST}|g" /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx && /admin-api/venv/bin/python /admin-api/admin.py'