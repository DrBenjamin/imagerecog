#!/usr/bin/env sh
# Starting the dev server with `&&` to ensure the first command runs successfully before starting the server
mcp dev src/server.py > /dev/null 2>&1 &

# Starting the server in the background
python src/server.py > /dev/null 2>&1 &

# Starting the Streamlit app
python -m streamlit run app.py --server.enableXsrfProtection false > /dev/null 2>&1 &