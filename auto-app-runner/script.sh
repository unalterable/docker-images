#!/bin/bash

WORKING_DIR=$(pwd)
REPO_DIR=$WORKING_DIR/repository
LOG_FILE=$WORKING_DIR/log.txt
echo "Creating logfile: $LOG_FILE"
touch $LOG_FILE

# Check if the repository exists by looking for .git directory
# This handles the case where the directory exists (due to volume) but has no repo
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Repository not found or empty." | tee -a $LOG_FILE

    echo "Starting setup server..." | tee -a $LOG_FILE
    node setupServer.js

    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Cloning the repo." | tee -a $LOG_FILE
    git clone --depth=1 --single-branch $(cat REPO_URL) $REPO_DIR
    
    # If the clone was into a subdirectory (some repos do this), move everything up
    if [ ! -d "$REPO_DIR/.git" ]; then
        echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Moving files from subdirectory." | tee -a $LOG_FILE
        # Find the first directory that has .git
        SUBDIRS=$(find $REPO_DIR -type d -name ".git" -exec dirname {} \; | head -n 1)
        if [ ! -z "$SUBDIRS" ]; then
            mv $SUBDIRS/* $REPO_DIR/
            mv $SUBDIRS/.* $REPO_DIR/ 2>/dev/null || true
            rmdir $SUBDIRS
        fi
    fi
fi

cd $REPO_DIR

EXIT_CODE=0
while [ $EXIT_CODE -eq 0 ]; do
    # git fetch
    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Git fetch." | tee -a $LOG_FILE
    git fetch --depth=1

    # Git reset to origin/main
    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Git reset to origin/main." | tee -a $LOG_FILE
    git reset --hard origin/main

    # Start the node process
    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Starting the process." | tee -a $LOG_FILE
    PORT=8080 npm start
    EXIT_CODE=$? 

    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: process ended with exit code: $EXIT_CODE" | tee -a $LOG_FILE
done

echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: EXIT" | tee -a $LOG_FILE
cd $WORKING_DIR
