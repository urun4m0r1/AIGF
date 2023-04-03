from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from utils.file_io import load_json


@dataclass
class Participant:
    role: str
    name: str
    nickname: Optional[str] = None


@dataclass
class Personality:
    category: str
    type: str


@dataclass
class Conversation:
    participants: List[Participant]
    personality: List[Personality]
    prompt: str
    creativity_level: int
    senders_swapped: bool


@dataclass
class Message:
    sender: str
    text: str
    timestamp: str


@dataclass
class Messages:
    messages: List[Message]


@dataclass
class TraitData:
    type: str
    sentences: List[str]


@dataclass
class CategoryData:
    category: str
    traits: List[TraitData]


@dataclass
class PersonalityData:
    categories: List[CategoryData]


class ConversationParser:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def parse(self) -> Conversation:
        participants_data = self.data['conversation']['participants']
        participants = [Participant(p['role'], p['name'], p.get('nickname')) for p in participants_data]
        personality_data = self.data['conversation']['personality']
        personality = [Personality(p['category'], p['type']) for p in personality_data]
        prompt = self.data['conversation']['prompt']
        creativity_level = self.data['conversation']['creativityLevel']
        senders_swapped = self.data['conversation']['sendersSwapped']

        return Conversation(participants, personality, prompt, creativity_level, senders_swapped)


class MessagesParser:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def parse(self) -> Messages:
        messages_data = self.data['messages']
        messages = [Message(m['sender'], m['text'], m['timestamp']) for m in messages_data]

        return Messages(messages)


class PersonalityParser:
    def __init__(self, prompt: Dict[str, Any]):
        self.prompt = prompt

    def parse(self) -> PersonalityData:
        personality_data = self.prompt['personality']

        categories = []
        for category_data in personality_data:
            category_name = category_data['category']
            traits_data = category_data['traits']

            traits = [TraitData(trait_data['type'], trait_data['sentences']) for trait_data in traits_data]
            categories.append(CategoryData(category_name, traits))

        return PersonalityData(categories)


class OutputGenerator:
    def __init__(self, conversation: Conversation, messages: Messages, personality: PersonalityData):
        self.conversation = conversation
        self.messages = messages
        self.personality = personality
        self.names = [p.name for p in self.conversation.participants]

    def get_category_sentences(self, personality: Personality) -> List[str]:
        return [f"{sentence.format(*self.names)}\n"
                for category in self.personality.categories
                if category.category == personality.category
                for trait in category.traits
                if trait.type == personality.type
                for sentence in trait.sentences]

    def get_personality_sentences(self, personality: List[Personality]) -> str:
        for p in personality:
            if p.type == 'none':
                continue

            sentences = self.get_category_sentences(p)
            if sentences:
                yield f"[{p.category.capitalize()}]\n{''.join(sentences)}\n"

    def get_complete_personality(self, personality: List[Personality]) -> str:
        return ''.join(self.get_personality_sentences(personality))

    def get_sender_name(self, sender: str) -> Optional[str]:
        return next((p.name for p in self.conversation.participants if p.role == sender), None)

    def format_names(self, message: str) -> str:
        return message.format(*self.names)

    def generate_output(self) -> str:
        # Extract personality
        personality_output = self.get_complete_personality(self.conversation.personality)

        # Extract additional
        additional_output = f"[Additional]\n{self.format_names(self.conversation.prompt)}\n\n"

        # Extract messages
        messages_output = '[Messages]\n' + ''.join(
            [f"{self.get_sender_name(m.sender)}: {m.text}\n" if self.get_sender_name(m.sender)
             else f"\n({m.text})\n\n"
             for m in self.messages.messages])

        return f"{personality_output}{additional_output}{messages_output}"


if __name__ == '__main__':
    dat = load_json('cache/1234567890.json')
    prom = load_json('prompt.json')

    conv_parser = ConversationParser(dat)
    conv = conv_parser.parse()

    msg_parser = MessagesParser(dat)
    msg = msg_parser.parse()

    pers_parser = PersonalityParser(prom)
    pers = pers_parser.parse()

    gen = OutputGenerator(conv, msg, pers)
    output = gen.generate_output()

    print(output)
