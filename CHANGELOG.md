# Change Log

All notable changes to the MCP server and client app for image recognition.

## [0.3.0]
- Added mobile App
    - Angular mobile app

## [0.2.0]
- Added resources
    - MCP server
        - get_static_image
            - get a static image from a file (Image.png)
        - get_variant_image
            - get a variant image from url (Image.png or Image2.png)
    - Stremalit App
        - displays the static image
        - displays the variant image


## [0.1.0]
- Initial release
    - MCP server
        - image_recognition tool:
            - get a description of an image
                - Ollama (locally) or OpenAI (remote)
            - get a thumbnail of an image
    - Stremalit App
        - takes an image as input
        - displays the image description
        - displays the image as thumbnail
