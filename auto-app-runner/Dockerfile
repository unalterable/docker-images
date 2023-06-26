# Use a base image with Bash installed
FROM node:latest

# Set the working directory
WORKDIR /app

# Install stuff
RUN apt-get update && apt-get install -y git

# Copy the script file to the working directory
COPY script.sh /app/script.sh
RUN chmod +x /app/script.sh

# Set the ENTRYPOINT to run the script
ENTRYPOINT ["/app/script.sh"]