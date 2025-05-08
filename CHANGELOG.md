# Change Log

All notable changes to the Agentic AI app.

## [0.1.0]
- Added mobile App
    - Angular mobile app
- Added MCP server
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
- Added Streamlit App
        - displays the static image
        - displays the variant image
        - takes an image as input
            - displays the image description
            - displays the image as thumbnail
