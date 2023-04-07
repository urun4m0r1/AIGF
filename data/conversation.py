# generated by datamodel-codegen:
#   filename:  conversation.yaml
#   timestamp: 2023-04-07T12:58:01+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Session(BaseModel):
    id: int
    language: str
    timezone: str
    creationTime: str


class Participant(BaseModel):
    role: str
    name: str
    nickname: Optional[str] = None


class Trait(BaseModel):
    category: str
    style: str


class Settings(BaseModel):
    participants: List[Participant]
    traits: List[Trait]
    userPrompt: str
    creativityLevel: int
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
