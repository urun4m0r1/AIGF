# generated by datamodel-codegen:
#   filename:  prompt.yaml
#   timestamp: 2023-04-07T12:58:00+00:00

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Choice(BaseModel):
    style: str
    prompts: List[str]


class Trait(BaseModel):
    category: str
    choices: List[Choice]


class Model(BaseModel):
    traits: List[Trait]
