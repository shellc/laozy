# Laozy

[English](./README.md) | [中文](./README_cn.md)

Laozy is an application used to build and deploy LLMs-based dialogue robots. 

It calls LLMs through LangChain to generate dialogues and integrates vector databases such as chromadb to build knowledge bases. Laozy provides prompt design and management, and the built dialogue robots can be published as services through RESTful interfaces, web, WeChat customer service, and other means.

![Arch](./assets/images/arch.png)

## Verson

* Current version: 0.0.1
* Status: Preview

### Features

| Feature | Description | Release |
| -- | -- | -- |
| gpt-3.5-turbo | Supported through Langchain | 0.0.1 |
| Knowledge base | Supported through chromadb in-memory | 0.0.1 |
| REST API | Document not yet complete | 0.0.1 |
| WeChat customer service| Supports access to WeChat customer service to provide robot dialogue | 0.0.1 |
| Installation and deployment | Under development

## Installtion

### Config

```
mkdir ~/.laozy
cp ./migrations/settings.ini ~/.laozy/settings.ini
```

### Install dependencies
```
pip3 install -r requirements.txt
```

### Setup database

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

## Main dependencies

* fastapi
* SQLAlchemy
* langchain
* openai
* chromadb

## Contribution

Welcome to contribute code and provide feedback.