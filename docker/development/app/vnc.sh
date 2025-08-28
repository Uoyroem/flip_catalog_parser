#!/bin/bash

Xvfb $DISPLAY -screen 0 $SCREEN_GEOMETRY &

x11vnc -display $DISPLAY -nopw -forever &

echo "VNC server started on port 5900."
echo "Using screen geometry: $SCREEN_GEOMETRY"
echo "Press Ctrl+C to stop."

wait -n