#!/usr/bin/env bash

RUN_DIR=./run
PID_FILE=$RUN_DIR/supergeneratorbot.pid
if [ ! -f $PID_FILE ]; then
  echo "pid file ($PID_FILE) not found!"
  exit 1
fi

kill $(cat $PID_FILE)
if [ $? -eq 0 ]; then
  rm -f $PID_FILE
else
  echo "kill failed"
  exit 2
fi

exit 0
