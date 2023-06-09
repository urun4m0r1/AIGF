# generated by datamodel-codegen:
#   filename:  conversation.yaml
#   timestamp: 2023-04-08T10:05:38+00:00

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Session(BaseModel):
    id: str
    language: str
    timezone: str
    creationTime: str


class Participant(BaseModel):
    role: str
    name: str


class Trait(BaseModel):
    category: str
    style: str


class Settings(BaseModel):
    participants: List[Participant]
    traits: List[Trait]
    userPrompt: str
    sendersSwapped: bool
    scrollAmount: int
    engineName: str
    maxTokens: int
    topP: int
    frequencyPenalty: float
    presencePenalty: float


class Message(BaseModel):
    sender: str
    text: str
    timestamp: str


class Model(BaseModel):
    session: Session
    settings: Settings
    messages: List[Message]
