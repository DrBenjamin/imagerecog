### `src/globals.py`
### Global variables for the Dateiablage application
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
## Imports
import wx
import os

# Setting elearning explorer
elearning_index = 0 # storing the index of the chosen item

# Setting file explorer
file_list = [] # storing the list of files in the File Explorer
file_path = None # storing the path of the selected file

# Setting MinIO credentials from wx.Config (user preferences) or environment variables
config = wx.Config("Dateiablage")
minio_endpoint = config.Read("minio_endpoint", os.environ.get("MINIO_ENDPOINT", "127.0.0.1:9000"))
minio_access_key = config.Read("minio_access_key", os.environ.get("MINIO_ACCESS_KEY", "<username>"))
minio_secret_key = config.Read("minio_secret_key", os.environ.get("MINIO_SECRET_KEY", "<password>"))
minio_secure = config.ReadBool("minio_secure", os.environ.get("MINIO_SECURE", "False") == "True")
minio_bucket_name = config.Read("minio_bucket_name", os.environ.get("MINIO_BUCKET", "<bucketname>"))

# Setting embedded Streamlit credentials from wx.Config (user preferences)
streamlit_endpoint = config.Read("streamlit_url", "127.0.0.1:8501")
streamlit_secure = config.ReadBool("streamlit_secure", False)