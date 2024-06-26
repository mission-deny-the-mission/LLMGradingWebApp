This app is a demo for grading student work using an LLM. This uses the Ollama API for running LLMs locally.
A docker image of this is available on the GitHub container registry at ghcr.io/mission-deny-the-mission/llmgradingwebapp:latest

This was implemented using Flask, SQLAlchemy, textract, and the ollama python module.
There is a docker-compose.yaml for use in testing the app. This is not intended for production use.