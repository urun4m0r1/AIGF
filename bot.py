from config import AppConfig
import conversation as conv
import discord
from discord import app_commands

config = AppConfig()
ai_conversation = conv.OpenAIConversation(config)


def reset_config():
    global config
    config = AppConfig()


def reset_conversation():
    global ai_conversation
    ai_conversation = conv.OpenAIConversation(config)


# Set intents to receive message content
intents = discord.Intents.default()
intents.message_content = True

# Create discord bot and command tree
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def run():
    print("Initializing Discord Bot...")
    client.run(config.bot_token)


@client.event
async def on_ready():
    print("Changing presence to online...")
    await client.change_presence(status=discord.Status.online, activity=None)

    print("Syncing server commands...")
    for guild in config.server_guilds:
        await tree.sync(guild=guild)

    print("Discord Bot is ready.")


async def stop():
    print("Changing presence to offline...")
    await client.change_presence(status=discord.Status.offline)

    print("Stopping Discord Bot...")
    await client.close()

    print("Discord Bot stopped.")


@tree.command(name="대화", description="인공지능과 대화", guilds=config.server_guilds)
@app_commands.describe(message="메시지")
async def __send_message(__interaction: discord.Interaction, message: str):
    print("Receiving message...")

    await __interaction.response.defer()
    __result = await ai_conversation.process(message)
    await __interaction.followup.send(__result)

    print("Message sent.")


@tree.command(name="정리", description="대화 내용 비우기", guilds=config.server_guilds)
async def __clear(__interaction: discord.Interaction):
    print("Clearing conversation...")

    ai_conversation.clear()
    await __interaction.response.send_message("[대화 내용이 비워졌습니다]")


@tree.command(name="초기화", description="설정 초기화", guilds=config.server_guilds)
async def __reset(__interaction: discord.Interaction):
    print("Resetting config and conversation...")

    reset_config()
    reset_conversation()
    await __interaction.response.send_message("[설정이 초기화되었습니다]")


@tree.command(name="이름", description="이름 변경", guilds=config.server_guilds)
@app_commands.describe(user="당신 이름", ai="상대 이름")
async def __rename(__interaction: discord.Interaction, user: str, ai: str):
    print(f"Renaming names...")
    __previous_user = config.user_name
    __previous_ai = config.ai_name
    ai_conversation.replace_name(user, ai)

    __message = f"""[이름이 변경되었습니다]
- 당신: {__previous_user} -> {user}
- 상대: {__previous_ai} -> {ai}"""
    await __interaction.response.send_message(__message)


# TODO: 전부 필수 인자가 아닌 선택적 인자로 변경
@tree.command(name="설정", description="설정 변경", guilds=config.server_guilds)
@app_commands.describe(
    creativity="창의력", intelligence="지능", personality="성격",
    mood="기분", reputation="평판", age="나이", relationship="관계", title="호칭", extra="추가 설정")
@app_commands.choices(
    creativity=conv.creativities, intelligence=conv.intelligences, personality=conv.persornalities,
    mood=conv.moods, reputation=conv.reputations, age=conv.ages, relationship=conv.relationships)
async def __config(__interaction: discord.Interaction,
                   creativity: int, intelligence: int, personality: int,
                   mood: int, reputation: int, age: int, relationship: int, title: str, extra: str):
    print("Changing config...")
    ai_conversation.change_creativity(creativity)
    ai_conversation.change_intelligence(intelligence)
    ai_conversation.change_personality(personality)
    ai_conversation.change_mood(mood)
    ai_conversation.change_reputation(reputation)
    ai_conversation.change_age(age)
    ai_conversation.change_relationship(relationship)
    ai_conversation.change_title(title)
    ai_conversation.change_extra(extra)

    ai_conversation.clear()

    __message = f"""[설정이 변경되었습니다]
- 창의력: {conv.creativities[creativity].name}
- 지능: {conv.intelligences[intelligence].name}
- 성격: {conv.persornalities[personality].name}
- 기분: {conv.moods[mood].name}
- 평판: {conv.reputations[reputation].name}
- 나이: {conv.ages[age].name}
- 관계: {conv.relationships[relationship].name}
- 호칭: {title}
- 추가 설정: {extra}"""
    await __interaction.response.send_message(__message)
