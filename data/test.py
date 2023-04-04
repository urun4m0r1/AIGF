from typing import Optional, List

from data import prompt, conversation
from data import prompt_parser, conversation_parser


class OutputGenerator:
    def __init__(self, prompt_model: prompt.Model, conversation_model: conversation.Model):
        self.prompt = prompt_model
        self.conversation = conversation_model

        self.settings = self.conversation.settings
        self.messages = self.conversation.messages

        self.participants = self.settings.participants
        self.user_traits = self.settings.traits

        self.traits = self.prompt.traits

        self.names = [p.name for p in self.participants]

    def get_category_sentences(self, user_trait) -> List[str]:
        return [f"{sentence.format(*self.names)}\n"
                for trait in self.traits
                if trait.category == user_trait.category
                for choice in trait.choices
                if choice.style == choice.style
                for sentence in choice.prompts]

    def get_personality_sentences(self) -> str:
        for user_trait in self.user_traits:
            if user_trait.style == 'none':
                continue

            sentences = self.get_category_sentences(user_trait)
            if sentences:
                yield f"[{user_trait.category.capitalize()}: {user_trait.style.capitalize()}]\n{''.join(sentences)}\n"

    def get_sender_name(self, sender: str) -> Optional[str]:
        return next((p.name for p in self.participants if p.role == sender), None)

    def format_names(self, message: str) -> str:
        return message.format(*self.names)

    def generate_result(self) -> str:
        # Extract personality
        personality_output = ''.join(self.get_personality_sentences())

        # Extract additional
        additional_output = f"[Note]\n{self.format_names(self.settings.userPrompt)}\n\n"

        # Extract messages
        messages_output = '[Messages]\n' + ''.join(
            [f"{self.get_sender_name(m.sender)}: {m.text}\n" if self.get_sender_name(m.sender)
             else f"\n({m.text})\n\n"
             for m in self.messages])

        return f"{personality_output}{additional_output}{messages_output}"


if __name__ == '__main__':
    prompt = prompt_parser.parse()
    conversation = conversation_parser.parse('../cache/1234567890.yaml')

    output = OutputGenerator(prompt, conversation)
    result = output.generate_result()

    print(result)
