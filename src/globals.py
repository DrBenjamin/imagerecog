### `src/globals.py`
### Global variables for the Dateiablage application
### Open-Source, hosted on https://github.com/DrBenjamin/Dateiablage
### Please reach out to ben@seriousbenentertainment.org for any questions
## Imports
import os

# e-Learning
file_path_elearning = None # storing the path to e-Learning definition file (CSV)
df_elearning = None # storing the dataframe of the e-Learning definition file
ticket_chosen = False # storing if a single ticket was chosen
elearning_index = 0 # storing the index of the chosen item

# Setting MinIO credentials from secrets or fallback
minio_endpoint = os.environ.get("MINIO_ENDPOINT", "127.0.0.1:9000")
minio_access_key = os.environ.get("MINIO_ACCESS_KEY", "<username>")
minio_secret_key = os.environ.get("MINIO_SECRET_KEY", "<password>")
minio_secure = os.environ.get("MINIO_SECURE", "False").lower() == "true"
minio_bucket_name = os.environ.get("MINIO_BUCKET", "<bucket_name>")

# Tasks
df_tasks = None # storing the dataframe of the tasks file

# File Explorer
file_list = [] # storing the list of files in the File Explorer
file_list_import = [] # storing the list of files to import in the eLearning
file_path = None # storing the path to the selected file in the File Explorer
folder_path = None # storing the path to the selected root folder for the File Explorer
folder_path_import = None # storing the path to the root folder for the eLearning import
folder_path_jira = None # storing the path to the JIRA tickets (multi file import)
folder_path_elearning = None # storing the path to the new e-Learning folder
root_folder_name = None # storing the name of the root folder for folder creation

# Preferences
mapping = False # needed for initial mapping of drive letter
