### `src/snowflake_connector.py`
### Snowflake Stage connector for BenBox
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import os
import streamlit as st
import snowflake.connector
import base64
import tempfile
from typing import Optional
from contextlib import contextmanager

class SnowflakeStageConnector:
    """Connector for Snowflake Stage operations"""
    
    def __init__(self):
        """Initialize Snowflake connection"""
        # Check if Snowflake config exists
        if 'SNOWFLAKE' not in st.secrets:
            raise ValueError("Snowflake configuration not found in Streamlit secrets")
            
        self.sf_config = st.secrets['SNOWFLAKE']
        self.conn = None
        
    @contextmanager
    def get_connection(self):
        """Create a new Snowflake connection or reuse existing one"""
        try:
            # Create a new connection if none exists
            if self.conn is None or self.conn.is_closed():
                self.conn = snowflake.connector.connect(
                    account=self.sf_config.get('ACCOUNT'),
                    user=self.sf_config.get('USER'),
                    ******'PASSWORD'),
                    warehouse=self.sf_config.get('WAREHOUSE'),
                    database=self.sf_config.get('DATABASE'),
                    schema=self.sf_config.get('SCHEMA')
                )
            yield self.conn
        finally:
            # Don't close connection here to allow reuse
            pass
            
    def get_file_from_stage(self, file_name: str) -> bytes:
        """Download a file from Snowflake Stage and return its contents as bytes"""
        stage_name = self.sf_config.get('STAGE')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create a temporary directory to store downloaded file
            with tempfile.TemporaryDirectory() as tmp_dir:
                local_file_path = os.path.join(tmp_dir, file_name)
                
                # Execute GET command to download file from stage
                get_command = f"GET @{stage_name}/{file_name} file://{local_file_path}"
                cursor.execute(get_command)
                
                # Read the downloaded file
                if os.path.exists(local_file_path):
                    with open(local_file_path, 'rb') as f:
                        file_bytes = f.read()
                    return file_bytes
                else:
                    raise FileNotFoundError(f"File {file_name} not found in stage {stage_name}")
                    
    def get_base64_from_stage(self, file_name: str) -> str:
        """Get a file from Snowflake Stage and return its base64-encoded string"""
        file_bytes = self.get_file_from_stage(file_name)
        return base64.b64encode(file_bytes).decode('utf-8')
        
    def list_files_in_stage(self) -> list:
        """List all files in the Snowflake Stage"""
        stage_name = self.sf_config.get('STAGE')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # List files in stage
            list_command = f"LIST @{stage_name}"
            cursor.execute(list_command)
            
            # Process results
            files = []
            for row in cursor:
                if len(row) > 0:
                    # Extract just the filename from the full path
                    file_path = row[0]
                    file_name = os.path.basename(file_path)
                    files.append(file_name)
                    
            return files