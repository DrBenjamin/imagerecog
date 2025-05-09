# Change Log

All notable changes to the Agentic AI app.

## [0.2.0]
- Added mobile App
    - Angular mobile app
- Added MCP server
    - get_country_name
        - get the country name from the country code
    - review_code
        - get a review of a code snippet
    - get_static_image
        - get a static image from a file (Image.png)
    - get_variant_image
        - get a variant image from url (Image.png or Image2.png)
    - image_recognition tool:
        - get a description of an image
            - Ollama (locally) or OpenAI (remote)
        - get a thumbnail of an image
- Added Streamlit dev app
        - converts country code into country name
        - displays the static image
        - displays the variant image
        - code review
        - takes an image as input
            - displays the image description
            - displays the image as thumbnail
        - RAG chatbot

[0.1.0]
- Initial release