### `src/globals.py`
### Global variables for the Dateiablage application
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
## Imports
import wx

# Setting elearning explorer
elearning_index = 0 # storing the index of the chosen item

# Setting file explorer
file_list = [] # storing the list of files in the File Explorer
file_path = None # storing the path of the selected file

# Setting MinIO credentials from wx.Config (user preferences)
config = wx.Config("Dateiablage")
minio_endpoint = config.Read("minio_endpoint", "host.docker.internal:9000")
minio_access_key = config.Read("minio_access_key", "<username>")
minio_secret_key = config.Read("minio_secret_key", "<password>")
minio_secure = config.ReadBool("minio_secure", False)
minio_bucket_name = config.Read("minio_bucket_name", "<bucket_name>")

# Setting embedded Streamlit credentials from wx.Config (user preferences)
streamlit_endpoint = config.Read("streamlit_url", "host.docker.internal:8501")
streamlit_secure = config.ReadBool("streamlit_secure", False)