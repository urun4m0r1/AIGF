@echo off
poetry run datamodel-codegen --input-file-type yaml --input prompt.yaml --output prompt.py
poetry run datamodel-codegen --input-file-type yaml --input conversation.yaml --output conversation.py