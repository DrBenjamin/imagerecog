### `src/server/get_country_name.py`
### MCP server tool for image recognition
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
import streamlit as st
from . import mcp
import mysql.connector
import logging
logger = logging.getLogger(__name__)


@mcp.tool()
async def get_country_name(country_code: str = None) -> str:
    """
    Getting the country name for  a given country code.

    Args:
        country_code(str): The country code to look up.


    Returns:
        str: The country full name in english.

    Raises:
        ValueError: If no matching country is found.
        Exception: For database connection errors.
    """
    # Setting up DB connection parameters from Streamlit secrets
    db_secrets = st.secrets["DB"]
    try:
        conn = mysql.connector.connect(
            host=db_secrets["DB_HOST"],
            port=db_secrets["DB_PORT"],
            user=db_secrets["DB_USER"],
            password=db_secrets["DB_PASSWORD"],
            database=db_secrets["DB_NAME"]
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise Exception("Could not connect to the database.")

    try:
        cursor = conn.cursor(dictionary=True)
        # Building query dynamically based on provided parameters
        if country_code :
            query = """
                SELECT `ShortName de` FROM stage$iso3166
                WHERE CODE = %s;
            """
            cursor.execute(query, (country_code,))
        else:
            raise ValueError("Country_code must be provided.")
        results = cursor.fetchall()
        if not results:
            logger.warning(f"No country found for code '{country_code}'.")
            raise ValueError(f"No country found for code '{country_code}'.")

        # Returning the German short name from the first row
        return results[0]["ShortName de"]
    except Exception as e:
        logger.error(f"Error querying country names: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
