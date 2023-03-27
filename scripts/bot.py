import discord
from discord import app_commands

from scripts import conversation as conv
from settings.config import AppConfig

config = AppConfig()
config.cache.load()
config.cache.save()

ai = conv.OpenAIConversation(config)


def reset_config():
    global config
    global ai

    config = AppConfig()
    config.cache.save()

    ai = conv.OpenAIConversation(config)


# Set intents to receive message content
intents = discord.Intents.default()
intents.message_content = True

# Create discord bot and command tree
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def run():
    print("[System] Initializing Discord Bot...")
    client.run(config.bot_token)


@client.event
async def on_ready():
    print("[Event] Changing presence to online...")
    await client.change_presence(status=discord.Status.online, activity=None)

    print("[Event] Syncing server commands...")
    for guild in config.server_guilds:
        try:
            await tree.sync(guild=guild)
        except discord.errors.Forbidden:
            print(f"[Event] Failed to sync commands in '{guild.id}' due to insufficient permissions.")

    print("[Event] Discord Bot is ready.")


async def stop():
    print("[System] Changing presence to offline...")
    await client.change_presence(status=discord.Status.offline)

    print("[System] Stopping Discord Bot...")
    await client.close()

    print("[System] Discord Bot stopped.")


def format_message(message: str, answer: str) -> str:
    user_name = config.cache.user_name
    ai_name = config.cache.ai_name
    return f"**{user_name}**: {message}\n**{ai_name}**: {answer}"


@tree.command(name="대화", description="인공지능과 대화", guilds=config.server_guilds)
@app_commands.describe(message="메시지")
async def _send_message(interaction: discord.Interaction, message: str):
    print("[Command] Receiving message...")

    await interaction.response.defer()
    answer = await ai.predict_answer(message)
    await interaction.followup.send(format_message(message, answer))

    print("[Command] Message sent.")


@tree.command(name="기록", description="대화 마지막에 이어서 문장을 삽입", guilds=config.server_guilds)
@app_commands.describe(prompt="프롬프트")
async def _record_prompt(interaction: discord.Interaction, prompt: str):
    print("[Command] Recording message...")

    ai.record_prompt(f"\n{prompt}\n\n")
    await interaction.response.send_message(f"[프롬프트가 기록되었습니다]\n{prompt}")


@tree.command(name="바꾸기", description="모든 대화에서 특정 단어를 치환", guilds=config.server_guilds)
@app_commands.describe(before="기존 단어", after="새 단어")
async def _replace_prompt_text(interaction: discord.Interaction, before: str, after: str):
    print("[Command] Replacing words...")

    ai.replace_prompt_text(before, after)
    await interaction.response.send_message(f"[단어를 치환했습니다]\n{before} -> {after}")


@tree.command(name="이름", description="이름 변경", guilds=config.server_guilds)
@app_commands.describe(user_name="당신 이름", ai_name="상대 이름")
async def _replace_names(interaction: discord.Interaction, user_name: str, ai_name: str):
    print("[Command] Renaming...")

    previous_user = config.cache.user_name
    previous_ai = config.cache.ai_name
    ai.replace_names(user_name, ai_name)

    message = f"""[이름이 변경되었습니다]
- 당신: {previous_user} -> {user_name}
- 상대: {previous_ai} -> {ai_name}"""
    await interaction.response.send_message(message)


@tree.command(name="정리", description="대화 내용 비우기", guilds=config.server_guilds)
async def _reset_prompt(interaction: discord.Interaction):
    print("[Command] Clearing conversation...")

    ai.reset_prompt()
    await interaction.response.send_message("[대화 내용이 비워졌습니다]")


@tree.command(name="초기화", description="설정 초기화", guilds=config.server_guilds)
async def _reset_config(interaction: discord.Interaction):
    print("[Command] Resetting config...")

    reset_config()
    ai.reset_prompt()
    await interaction.response.send_message("[모든 설정이 초기화되었습니다]")


@tree.command(name="설정", description="설정 변경 (아직 창의력 빼고 작동 안함)", guilds=config.server_guilds)
@app_commands.describe(creativity="창의력",
                       intelligence="지능",
                       personality="성격",
                       mood="기분",
                       reputation="평판",
                       age="나이",
                       relationship="관계",
                       title="호칭",
                       extra="추가 설정")
@app_commands.choices(creativity=conv.creativities,
                      intelligence=conv.intelligences,
                      personality=conv.persornalities,
                      mood=conv.moods,
                      reputation=conv.reputations,
                      age=conv.ages,
                      relationship=conv.relationships)
async def _config(interaction: discord.Interaction,
                  creativity: int = None,
                  intelligence: int = None,
                  personality: int = None,
                  mood: int = None,
                  reputation: int = None,
                  age: int = None,
                  relationship: int = None,
                  title: str = None,
                  extra: str = None):
    print("[Command] Changing config...")

    content = ""
    if creativity is not None:
        ai.change_creativity(creativity)
        content += f"- 창의력: {conv.creativities[creativity].name}"
    if intelligence is not None:
        ai.change_intelligence(intelligence)
        content += f"- 지능: {conv.intelligences[intelligence].name}"
    if personality is not None:
        ai.change_personality(personality)
        content += f"- 성격: {conv.persornalities[personality].name}"
    if mood is not None:
        ai.change_mood(mood)
        content += f"- 기분: {conv.moods[mood].name}"
    if reputation is not None:
        ai.change_reputation(reputation)
        content += f"- 평판: {conv.reputations[reputation].name}"
    if age is not None:
        ai.change_age(age)
        content += f"- 나이: {conv.ages[age].name}"
    if relationship is not None:
        ai.change_relationship(relationship)
        content += f"- 관계: {conv.relationships[relationship].name}"
    if title is not None:
        ai.change_title(title)
        content += f"- 호칭: {title}"
    if extra is not None:
        ai.change_extra(extra)
        content += f"- 추가 설정: {extra}"

    message = f"[설정이 변경되었습니다]\n{content}"
    await interaction.response.send_message(message)

# TODO: 인격 슬롯 3개 변경 가능하게 추가
# TODO: 리롤 버튼 추가
