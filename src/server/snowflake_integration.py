### MCP server tool for Snowflake vector store integration
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import os
import base64
import json
import snowflake.connector
import streamlit as st
from . import mcp

# Global Snowflake connection (singleton pattern)
class SnowflakeConnection:
    _instance = None

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            try:
                self.conn = snowflake.connector.connect(
                    user=st.secrets['Snowflake']['user'],
 
                    account=st.secrets['Snowflake']['account'],
                    warehouse=st.secrets['Snowflake']['warehouse'],
                    database=st.secrets['Snowflake']['database'],
                    schema=st.secrets['Snowflake']['schema']
                )
                self.cursor = self.conn.cursor()
            except Exception as e:
                self.conn = None
                self.cursor = None
                print(f'Error connecting to Snowflake: {e}')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SnowflakeConnection()
        return cls._instance

# Global Snowflake connection instance
snowflake_conn = SnowflakeConnection.get_instance()

@mcp.tool(name='create_vector_content', description='Upload files to Snowflake vector store')
def create_vector_content(file_content: str, file_name: str) -> str:
    """Create bucket/stage files in the Snowflake vector store."""
    try:
        if not snowflake_conn.conn:
            return json.dumps({
                'success': False,
                'message': 'Failed to connect to Snowflake. Check your connection settings.'
            })

        # Decode the base64 file content if applicable
        file_bytes = base64.b64decode(file_content) if ';base64,' in file_content else file_content.encode('utf-8')

        # 1. Retrieve files from the bucket/stage
        snowflake_conn.cursor.execute('LIST @MY_STAGE')
        stage_files = snowflake_conn.cursor.fetchall()
        
        # 2. Store the file in a temporary location
        temp_file_path = f'/tmp/{file_name}'
        with open(temp_file_path, 'wb') as f:
            f.write(file_bytes)
        
        # 3. Upload the file to Snowflake stage
        snowflake_conn.cursor.execute(f'PUT file://{temp_file_path} @MY_STAGE')
        
        # 4. Load the file into the vector store
        snowflake_conn.cursor.execute(f"""
            INSERT INTO vector_store (file_name, file_content, embedding)
            SELECT '{file_name}', 
                   FILE_CONTENT,
                   VECTOR_EMBED(FILE_CONTENT)
            FROM @MY_STAGE/{file_name}
        """)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        return json.dumps({
            'success': True,
            'message': f'Successfully uploaded {file_name} to Snowflake vector store.'
        })
        
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'Error: {str(e)}'
        })
                    ******'Snowflake']['password'],
