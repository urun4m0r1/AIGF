from typing import Optional, Iterator, Iterable, List

from data import prompt, conversation
from data.conversation import Trait as UserTrait, Message
from data.prompt import Trait, Choice
from utils.iteration import trim


class History:
    def __init__(
            self,
            default_prompt: str,
            prompt_model: prompt.Model,
            conversation_model: conversation.Model
    ) -> None:
        self.default_prompt = default_prompt
        self.prompt_model = prompt_model
        self.conversation_model = conversation_model

    @property
    def traits(self) -> List[Trait]:
        return self.prompt_model.traits

    @traits.setter
    def traits(self, traits: List[Trait]) -> None:
        self.prompt_model.traits = traits

    @property
    def session(self) -> conversation.Session:
        return self.conversation_model.session

    @session.setter
    def session(self, session: conversation.Session) -> None:
        self.conversation_model.session = session

    @property
    def settings(self) -> conversation.Settings:
        return self.conversation_model.settings

    @settings.setter
    def settings(self, settings: conversation.Settings) -> None:
        self.conversation_model.settings = settings

    @property
    def messages(self) -> List[Message]:
        return self.conversation_model.messages

    @messages.setter
    def messages(self, messages: List[Message]) -> None:
        self.conversation_model.messages = messages

    @property
    def participants(self) -> List[conversation.Participant]:
        return self.settings.participants

    @participants.setter
    def participants(self, participants: List[conversation.Participant]) -> None:
        self.settings.participants = participants

    @property
    def user_traits(self) -> List[UserTrait]:
        return self.settings.traits

    @user_traits.setter
    def user_traits(self, user_traits: List[UserTrait]) -> None:
        self.settings.traits = user_traits

    def get_prompt_history(self) -> str:
        full_prompt = self.get_full_prompt()
        full_messages = self.get_full_messages()

        contents = trim((full_prompt, full_messages))
        return '\n\n'.join(contents)

    def get_full_prompt(self) -> str:
        default_prompt_section = self.default_prompt
        prompt_sections = self.get_prompt_sections()
        user_prompt_section = self.get_user_prompt_section()
        prompts = trim((default_prompt_section, *prompt_sections, user_prompt_section))

        names = (p.name for p in self.participants)
        return '\n\n'.join(prompts).format(*names)

    def get_prompt_sections(self) -> Iterator[str]:
        for user_trait in self.user_traits:
            prompt_section = self.get_prompt_section(user_trait)
            if prompt_section:
                yield prompt_section

    def get_user_prompt_section(self) -> str:
        user_prompt = self.settings.userPrompt
        return f"[Note]\n{user_prompt}" if user_prompt else ''

    def get_prompt_section(self, user_trait: UserTrait) -> str:
        sentences = self.get_prompt(user_trait)
        if not sentences:
            return ''

        category = user_trait.category.capitalize()
        style = user_trait.style.capitalize()

        return f"[{category}: {style}]\n{sentences}"

    def get_prompt(self, user_trait: UserTrait) -> str:
        if user_trait.style == 'none':
            return ''

        trait = self.get_trait(user_trait.category)
        if not trait:
            return ''

        choice = self.get_choice(trait.choices, user_trait.style)
        if not choice:
            return ''

        return '\n'.join(choice.prompts) if choice.prompts else ''

    def get_trait(self, category: str) -> Optional[Trait]:
        return next((trait for trait in self.traits if trait.category == category), None)

    def get_choice(self, choices: Iterable[Choice], style: str) -> Optional[Choice]:
        return next((choice for choice in choices if choice.style == style), None)

    def get_full_messages(self) -> str:
        full_message = '\n'.join(self.format_message(message) for message in self.messages)
        if not full_message:
            return "[Messages]"

        return f"[Messages]\n{full_message}"

    def format_message(self, message: Message) -> str:
        sender_name = self.get_sender_name(message.sender)
        if sender_name:
            return f"{sender_name}: {message.text}"
        else:
            return f"\n({message.text})\n"

    def get_sender_name(self, sender: str) -> Optional[str]:
        return next((p.name for p in self.participants if p.role == sender), None)
