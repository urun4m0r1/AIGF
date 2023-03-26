from config import AppConfig
from conversation import OpenAIConversation
import discord
from discord import app_commands

config = AppConfig()
conversation = OpenAIConversation(config)


def reset_config():
    global config
    config = AppConfig()


def reset_conversation():
    global conversation
    conversation = OpenAIConversation(config)


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
    print(f"Received message: {message}")

    await __interaction.response.defer()
    __result = await conversation.process(message)
    await __interaction.followup.send(__result)

    print(f"Sent message: {__result}")


@tree.command(name="정리", description="대화 내용 비우기", guilds=config.server_guilds)
async def __clear(__interaction: discord.Interaction):
    print("Clearing conversation...")

    conversation.clear()
    await __interaction.response.send_message("대화 내용이 비워졌습니다.")


@tree.command(name="이름", description="이름 변경", guilds=config.server_guilds)
@app_commands.describe(user="유저 이름", ai="AI 이름")
async def __rename(__interaction: discord.Interaction, user: str, ai: str):
    print(f"Renaming user: {user} and AI: {ai}")

    config.user_name = user
    config.ai_name = ai

    conversation.clear()
    await __interaction.response.send_message("설정이 변경되었습니다.")


@tree.command(name="설정", description="설정 변경", guilds=config.server_guilds)
@app_commands.describe(engine="EngineName", temperature="Temperature", tokens="MaxTokens", p="TopP",
                       frequency="FrequencyPenalty", presence="PresencePenalty")
async def __config(__interaction: discord.Interaction,
                   engine: str, temperature: float, tokens: int, p: float, frequency: float, presence: float):
    print(f"Changing config: {engine}, {temperature}, {tokens}, {p}, {frequency}, {presence}")

    config.engine_name = engine
    config.temperature = temperature
    config.max_tokens = tokens
    config.top_p = p
    config.frequency_penalty = frequency
    config.presence_penalty = presence

    conversation.clear()
    await __interaction.response.send_message("설정이 변경되었습니다.")


@tree.command(name="초기화", description="설정 초기화", guilds=config.server_guilds)
async def __clear(__interaction: discord.Interaction):
    print("Resetting config and conversation...")

    reset_config()
    reset_conversation()
    await __interaction.response.send_message("설정이 초기화되었습니다.")
