### `src/server/minio.py`
### Embedding class for Snowflake
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import streamlit as st
import logging
from minio import Minio
from minio.error import S3Error
logger = logging.getLogger(__name__)

# Setting up MinIO client from Streamlit secrets
def get_minio_client():
    """Creating and returning a MinIO client using Streamlit secrets."""
    return Minio(
        endpoint=st.secrets["MinIO"]["endpoint"].replace("http://", ""),
        access_key=st.secrets["MinIO"]["access_key"],
        secret_key=st.secrets["MinIO"]["secret_key"],
        secure=False
    )

# Function to list buckets
def list_buckets(minio_client):
    try:
        buckets = minio_client.list_buckets()
        # Returning bucket names as lowercase and hyphenated for MinIO compatibility
        return [
            bucket.name.lower().replace(' ', '-')
            for bucket in buckets
        ]
    except S3Error as e:
        st.error(f"Error: {e}")
    return

# Function to list objects in a bucket
def list_objects(minio_client, bucket_name):
    # Ensuring bucket_name is lowercase and hyphenated for MinIO
    bucket_name = bucket_name.lower().replace(' ', '-')
    try:
        objects = minio_client.list_objects(bucket_name, recursive=True)
        return [
            obj.object_name
            for obj in objects
        ]
    except S3Error as e:
        st.error(f"Error: {e}")
    return
