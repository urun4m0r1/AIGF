import os
import openai
openai.organization = "ORGANIZATION_ID"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()