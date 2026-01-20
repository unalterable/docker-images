# Use OpenResty (nginx + LuaJIT + resty crypto libs)
FROM openresty/openresty:alpine

# Install Python, Flask, Apache utils
RUN apk add --no-cache openssl python3 py3-pip apache2-utils && \
    python3 -m venv /admin-api/venv && \
    /admin-api/venv/bin/pip install --upgrade pip && \
    /admin-api/venv/bin/pip install flask

# Copy Nginx configuration
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# Copy login page
RUN mkdir -p /etc/nginx/html
COPY login.html /etc/nginx/html/login.html

# Generate self-signed certs
RUN mkdir -p /etc/nginx/certs && \
    openssl genpkey -algorithm RSA -out /etc/nginx/certs/server.key -pkeyopt rsa_keygen_bits:2048 && \
    openssl req -new -x509 -key /etc/nginx/certs/server.key -out /etc/nginx/certs/server.crt -days 365 \
      -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost" \
      -addext "subjectAltName = IP:127.0.0.1"

# Copy htpasswd file
COPY .htpasswd /etc/nginx/.htpasswd

# Copy the Flask admin app
COPY admin-api.py /admin-api/admin.py

# Create directories for Let's Encrypt challenges and OpenResty logs
RUN mkdir -p /var/www/.well-known/acme-challenge && \
    mkdir -p /var/log/openresty && \
    mkdir -p /etc/nginx/secrets

# Initialize secrets with random values
RUN openssl rand -hex 32 > /etc/nginx/secrets/session_secret && \
    openssl rand -hex 32 > /etc/nginx/secrets/refresh_secret && \
    chmod 600 /etc/nginx/secrets/*

# Expose ports
EXPOSE 443 5000

# Start both OpenResty and Flask API
CMD sh -c '\
    sed "s|\$UPSTREAM_HOST|${UPSTREAM_HOST}|g" \
    /etc/nginx/nginx.conf.template > /usr/local/openresty/nginx/conf/nginx.conf && \
    /usr/local/openresty/nginx/sbin/nginx && \
    /admin-api/venv/bin/python /admin-api/admin.py'