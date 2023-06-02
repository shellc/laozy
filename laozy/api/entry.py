from fastapi import FastAPI

description = """
Laozy is a self-hosted web application that helps you build and deploy LLM-based dialogue robots.

The robot you built can connect to instant messaging platforms like WeChat, Telegram, etc. You can also integrate it into your app with REST APIs.
"""

tags_metadata = [
    {
        "name": "User",
        "description": "The module allows users to register and complete the authentication process, which is necessary for many of Laozy's features to work properly."
    },
    {
        "name": "Connector",
    },
    {
        "name": "Route",
    },
    {
        "name": "Channel",
    },
    {
        "name": "Robot",
    },
    {
        "name": "Prompt",
    },
    {
        "name": "Knowledge Base",
    },
    {
        "name": "Message",
    },
    {
        "name": "WeChat",
        "description": "Oprations with WeChat"
    },
]

entry = FastAPI(
    title="Laozy",
    version="0.1",
    description=description,
    openapi_tags=tags_metadata,
    contact={
        'name': 'shellc',
        'url': 'https://github.com/shellc/laozy'
    },
    docs_url=None,
    redoc_url='/docs'
)