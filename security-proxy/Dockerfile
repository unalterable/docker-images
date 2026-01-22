# Use OpenResty (nginx + LuaJIT + resty crypto libs)
FROM openresty/openresty:alpine

# Install dependencies
RUN apk add --no-cache \
    openssl \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    make \
    git

# Install lua-resty-bcrypt
RUN /usr/local/openresty/bin/opm get jkeys089/lua-resty-bcrypt

# Create Python venv and install Flask + bcrypt
RUN python3 -m venv /admin-api/venv && \
    /admin-api/venv/bin/pip install --upgrade pip && \
    /admin-api/venv/bin/pip install flask bcrypt

# Clean up build dependencies
RUN apk del gcc musl-dev python3-dev libffi-dev make git

# Copy Lua auth module
RUN mkdir -p /etc/nginx/lua
COPY lua/auth.lua /etc/nginx/lua/auth.lua

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

# Copy htpasswd file (bcrypt hashes)
COPY .htpasswd /etc/nginx/.htpasswd

# Copy the Flask admin app
COPY admin-api.py /admin-api/admin.py

# Create runtime directories
RUN mkdir -p /var/www/.well-known/acme-challenge \
             /var/log/openresty \
             /etc/nginx/secrets

# Initialize secrets
RUN openssl rand -hex 32 > /etc/nginx/secrets/session_secret && \
    openssl rand -hex 32 > /etc/nginx/secrets/refresh_secret && \
    chmod 644 /etc/nginx/secrets/*

EXPOSE 443 5000

CMD sh -c '\
    sed "s|\$UPSTREAM_HOST|${UPSTREAM_HOST}|g" \
    /etc/nginx/nginx.conf.template > /usr/local/openresty/nginx/conf/nginx.conf && \
    /usr/local/openresty/nginx/sbin/nginx && \
    /admin-api/venv/bin/python /admin-api/admin.py'