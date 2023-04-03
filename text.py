from typing import Dict, List, Optional

from utils.file_io import load_json


class Conversation:
    def __init__(self, data: Dict):
        self.participants = data['conversation']['participants']
        self.names = [p['name'] for p in self.participants]
        self.personality = data['conversation']['personality']
        self.prompt = data['conversation']['prompt']
        self.messages = data['messages']


class Personality:
    def __init__(self, prompt: Dict, names: List[str]):
        self.personality = prompt['personality']
        self.categories = {p['category']: p for p in self.personality}
        self.names = names

    def get_category_sentences(self, category: str, trait_type: str) -> List[str]:
        return [f'{sentence.format(*self.names)}\n'
                for traits in self.categories[category]['traits']
                for sentence in traits['sentences']
                if traits['type'] == trait_type]

    def get_personality_sentences(self, types: Dict[str, str]) -> str:
        for category, trait_type in types.items():
            if trait_type == 'none':
                continue

            sentences = self.get_category_sentences(category, trait_type)
            if sentences:
                yield f"[{category.capitalize()}]\n{''.join(sentences)}\n"

    def get_complete_personality(self, personality: List[Dict]) -> str:
        return ''.join(self.get_personality_sentences({p['category']: p['type'] for p in personality}))


class OutputGenerator:
    def __init__(self, conversation: Conversation, personality: Personality):
        self.conversation = conversation
        self.personality = personality

    def get_sender_name(self, sender: str) -> Optional[str]:
        return next((p['name'] for p in self.conversation.participants if p['role'] == sender), None)

    def generate_output(self) -> str:
        # Extract personality
        personality_output = self.personality.get_complete_personality(self.conversation.personality)

        # Extract additional
        additional_output = f"[Additional]\n{self.conversation.prompt.format(*self.conversation.names)}\n\n"

        # Extract messages
        messages_output = '[Messages]\n' + ''.join(
            [f"{self.get_sender_name(msg['sender'])}: {msg['text']}\n" if self.get_sender_name(msg['sender'])
             else f"\n({msg['text']})\n\n"
             for msg in self.conversation.messages])

        return personality_output + additional_output + messages_output


if __name__ == '__main__':
    conv = Conversation(load_json('cache/1234567890.json'))
    pers = Personality(load_json('prompt.json'), conv.names)
    gen = OutputGenerator(conv, pers)
    output = gen.generate_output()

    print(output)
