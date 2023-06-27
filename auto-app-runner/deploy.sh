#!/bin/bash

# Retrieve the tag argument from the command line
VERSION="$1"
REPOSITORY=unalterable/auto-app-runner
TAG=$REPOSITORY:$VERSION

echo $TAG

# Build the Docker image
docker build -t $TAG .

# Push the Docker image to the repository
docker push $TAG