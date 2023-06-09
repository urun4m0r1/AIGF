# generated by datamodel-codegen:
#   filename:  prompt.yaml
#   timestamp: 2023-04-08T10:05:28+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Choice(BaseModel):
    style: str
    prompts: Optional[List[str]] = None


class Trait(BaseModel):
    category: str
    choices: List[Choice]


class Model(BaseModel):
    traits: List[Trait]
