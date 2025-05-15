#!/bin/sh
# Setting up environment variables for Streamlit
export DISPLAY=:$DISPLAY_NUM

# Starting Xvfb
Xvfb :$DISPLAY_NUM -screen 0 ${WIDTH}x${HEIGHT}x24 &

# Starting x11vnc
x11vnc -display :$DISPLAY_NUM -forever -nopw -shared -bg

# Starting noVNC
novnc_proxy --vnc localhost:5900 --listen 6080 &

# Starting Phoenix app (compiled version)
./dist/Dateiablage/Dateiablage
