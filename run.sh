#!/usr/bin/env sh
# Activating micromamba environment
eval "$(micromamba shell hook -s posix)"
micromamba activate benbox

# Starting the dev server with `&&` to ensure the first command runs successfully before starting the server
mcp dev src/server.py > /dev/null 2>&1 &

# Starting the server in the background
python src/server.py > /dev/null 2>&1 &

# Starting the Streamlit app
#python -m streamlit run app.py --server.enableXsrfProtection false
