#!/bin/bash

WORKING_DIR=$(pwd)
REPO_DIR=$WORKING_DIR/repository
# RESET_REQUEST_FILE=$($WORKING_DIR)/repository/.REQUEST_RESET
# RESET_IGNORE_FILE=$($WORKING_DIR)/repository/.RESET_IGNORE
LOG_FILE=$WORKING_DIR/log.txt
echo "Creating logfile: $LOG_FILE"
touch $LOG_FILE

while [ ! -d $REPO_DIR ]; do
    # # Start a server in the background
    # echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Start a server in the background." | tee -a $LOG_FILE
    # nc -l -p "$PORT" < "$LOG_FILE" &
    # SERVER_PID=$!

    echo "Starting setup server..." | tee -a $LOG_FILE
    node setupServer.js

    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Cloning the repo." | tee -a $LOG_FILE
    git clone --depth=1 --single-branch $(cat REPO_URL) $REPO_DIR
done

cd $REPO_DIR

EXIT_CODE=0
while [ ! $EXIT_CODE -ne 0 ]; do
    # If requested, clear the directory
    # if [ -f $RESET_IGNORE_FILE ]; then
    #     echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: REQUEST_RESET file ($RESET_REQUEST_FILE) detected. Cleaning directory." | tee -a /app/log.txt
    #     find $REPO_DIR -type f -o -type d | grep -v -f <(if [ -f $RESET_IGNORE_FILE ]; then cat $RESET_IGNORE_FILE; fi) | xargs rm -rf
    # fi

    # Checkout to HEAD
    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Checkout to HEAD." | tee -a $LOG_FILE
    git fetch --depth=1 && git checkout HEAD

    # Start the node process
    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: Starting the process." | tee -a $LOG_FILE
    PORT=8080 npm start
    EXIT_CODE=$? 

    # Write time and exit code to file

    # if [ $EXIT_CODE -ne 0 ]; then
    #     echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: process ended with bad exit code: so exiting." | tee -a $LOG_FILE
    #     break
    # fi

    echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: process ended with exit code: $EXIT_CODE" | tee -a $LOG_FILE
done

echo "Time: $(date +"%Y-%m-%d %H:%M:%S"), Event: EXIT" | tee -a $LOG_FILE
cd $WORKING_DIR