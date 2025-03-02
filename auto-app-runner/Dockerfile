# Use a base image with Bash installed
FROM node:latest

# Set the working directory
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git

# Create the repository directory
RUN mkdir -p /app/repository

# Copy the all files to the working directory
COPY . /app

# Full access to script.sh
RUN chmod +x /app/script.sh

# Create a volume for the repository directory
VOLUME ["/app/repository"]

# Set the ENTRYPOINT to run the script
ENTRYPOINT ["/app/script.sh"]
