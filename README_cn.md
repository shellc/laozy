# Laozy

[English](./README.md) | [中文](./README_cn.md)

Laozy 是一个用于构建和部署基于 LLMs 对话机器人的应用。

通过 LangChain 调用 LLMs 生成对话，集成 chromadb 等向量数据库构建知识库。Laozy 提供 Prompt 设计和管理，构建的对话机器人可以通过 RESTful 接口、Web、微信客服等方式作为服务发布。

![Arch](./assets/images/arch.png)

## 版本

* 当前版本: 0.0.1
* 版本状态: 功能预览

### 功能

| 功能 | 描述 | 发布版本 |
| -- | -- | -- |
| gpt-3.5-turbo | 通过 Langchain 支持 | 0.0.1 |
| 知识库 | 通过 chromadb 内存版本支持 | 0.0.1 |
| REST API | 文档未完善 | 0.0.1 |
| 微信客服 | 支持接入微信客服提供机器人对话 | 0.0.1 |
| 安装部署 | 未完善 |  |

## 安装

### 配置

```
mkdir ~/.laozy
cp ./migrations/settings.ini ~/.laozy/settings.ini
```

### 安装依赖
```
pip3 install -r requirements.txt
```

### 初始化数据库

```
alembic -c ./migrations/alembic.ini revision --autogenerate
alembic -c ./migrations/alembic.ini upgrade head
```

### 启动服务

```
export PYTHONPATH=.
./bin/laozy
```

## 界面截屏

|  |  |  |  |
| :--:  | :--:  | :--:  | :--: |
| <img src="./assets/images/stock_analysis.png" alt="Stock Analysis" /> | <img src="./assets/images/knowledge_base.png" alt="Knowledge Base" /> | <img src="./assets/images/translator.png" alt="Translator" /> | <img src="./assets/images/prompts.png" alt="Prompting" /> | 
| 股票分析 | 知识库 | 翻译 | Prompting |
| <img src="./assets/images/doctor_assistant.png" alt="Doctor assistant"/> | <img src="./assets/images/friend.png" alt="Friend" /> | <img src="./assets/images/robot.png" alt="Robot" />| <img src="./assets/images/wxkf.jpeg" alt="Wechat Customer Service" height="120"/> |  |
| 医生助手 | 个人玩伴 | 对话机器人配置 | 微信客服 | 

## 主要依赖

* fastapi
* SQLAlchemy
* langchain
* openai
* chromadb

## 贡献

欢迎贡献代码、提供反馈。