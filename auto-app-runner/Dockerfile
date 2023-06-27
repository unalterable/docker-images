# Use a base image with Bash installed
FROM node:latest

# Set the working directory
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git

# Copy the all files to the working directory
COPY . /app

# Full access to script.sh
RUN chmod +x /app/script.sh

# Set the ENTRYPOINT to run the script
ENTRYPOINT ["/app/script.sh"]