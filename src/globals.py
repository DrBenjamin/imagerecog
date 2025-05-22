### `src/globals.py`
### Global variables for the BenBox application
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
## Imports
import wx
import os

# Creating a wx.Config object to store user preferences
config = wx.Config("BenBox")

# Setting Snowflake or MinIO
snowflake = config.ReadBool("snowflake", True) # storing the choice of Snowflake or MinIO

# Setting elearning explorer
elearning_index = 0 # storing the index of the chosen item

# Setting file explorer
file_list = [] # storing the list of files in the File Explorer
file_path = None # storing the path of the selected file

# Setting Snowflake credentials from wx.Config (user preferences) or environment variables
snowflake_user = config.Read("snowflake_user", os.environ.get("SNOWFLAKE_USER", ""))
snowflake_account = config.Read("snowflake_account", os.environ.get("SNOWFLAKE_ACCOUNT", ""))
snowflake_warehouse = config.Read("snowflake_warehouse", os.environ.get("SNOWFLAKE_WAREHOUSE", ""))
snowflake_database = config.Read("snowflake_database", os.environ.get("SNOWFLAKE_DATABASE", ""))
snowflake_schema = config.Read("snowflake_schema", os.environ.get("SNOWFLAKE_SCHEMA", ""))
snowflake_role = config.Read("snowflake_role", os.environ.get("SNOWFLAKE_ROLE", ""))
snowflake_private_key_file = config.Read("snowflake_private_key_file", os.environ.get("SNOWFLAKE_PRIVATE_KEY_FILE", ""))

# Setting MinIO credentials from wx.Config (user preferences) or environment variables
minio_endpoint = config.Read("minio_endpoint", os.environ.get("MINIO_ENDPOINT", "127.0.0.1:9000"))
minio_access_key = config.Read("minio_access_key", os.environ.get("MINIO_ACCESS_KEY", "<username>"))
minio_secret_key = config.Read("minio_secret_key", os.environ.get("MINIO_SECRET_KEY", "<password>"))
minio_secure = config.ReadBool("minio_secure", os.environ.get("MINIO_SECURE", "False") == "True")
minio_bucket_name = config.Read("minio_bucket_name", os.environ.get("MINIO_BUCKET", "<bucketname>"))

# Setting embedded Streamlit credentials from wx.Config (user preferences)
streamlit_endpoint = config.Read("streamlit_url", "http://streamlit:8501")
streamlit_secure = config.ReadBool("streamlit_secure", False)