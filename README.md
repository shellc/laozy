# Laozy

[English](./README.md) | [中文](./README_cn.md)

Laozy is a self-hosted web application that helps you build and deploy LLM-based dialogue robots.

The robot you built can connect to instant messaging platforms like WeChat, Telegram, etc. You can also integrate it into your app with REST APIs.

![Arch](./assets/images/arch.png)

## Version

* Current version: 0.0.1
* Status: Preview

### Features

| Feature | Description | Release |
| -- | -- | -- |
| gpt-3.5-turbo | Langchain | 0.0.1 |
| Knowledge base | chromadb in-memory | 0.0.1 |
| REST API | Document not yet completed | 0.0.1 |
| WeChat Customer Service| Connect robot to WeChat Customer Service | 0.0.1 |
| Installation and deployment | Under development |

## Installtion

### Configuration

```
mkdir ~/.laozy
cp ./migrations/settings.ini ~/.laozy/settings.ini
```

### Install Dependencies
```
pip3 install -r requirements.txt
```

### Setup Database

```
alembic -c ./migrations/alembic.ini revision --autogenerate
alembic -c ./migrations/alembic.ini upgrade head
```

### Start

```
export PYTHONPATH=.
./bin/laozy
```

## Screenshots

|  |  |  |  |
| :--:  | :--:  | :--:  | :--: |
| <img src="./assets/images/stock_analysis.png" alt="Stock Analysis" /> | <img src="./assets/images/knowledge_base.png" alt="Knowledge Base" /> | <img src="./assets/images/translator.png" alt="Translator" /> | <img src="./assets/images/prompts.png" alt="Prompting" /> | 
| Stock analysis | Knowledge base | Translator | Prompting |
| <img src="./assets/images/doctor_assistant.png" alt="Doctor assistant"/> | <img src="./assets/images/friend.png" alt="Friend" /> | <img src="./assets/images/robot.png" alt="Robot" />| <img src="./assets/images/wxkf.jpeg" alt="Wechat Customer Service" height="120"/> |  |
| Doctor's assitant | Playmate | Conversation bot configuration | WeChat Customer Service | 

## Dependencies

* fastapi
* SQLAlchemy
* langchain
* openai
* chromadb

## Contribution

Welcome to contribute code and provide feedback.