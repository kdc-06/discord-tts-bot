import os
import asyncio
import tempfile
import aiohttp
import discord
from discord.ext import commands

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")
FISH_AUDIO_MODEL_ID = os.getenv("FISH_AUDIO_MODEL_ID")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

tts_lock = asyncio.Lock()


@bot.event
async def on_ready():
    print(f"봇 로그인 성공: {bot.user}")
    print("TTS 봇이 준비되었습니다.")


async def make_tts(text):
    url = "https://api.fish.audio/v1/tts"

    headers = {
        "Authorization": f"Bearer {FISH_AUDIO_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "text": text,
        "model": "s2-pro",
        "reference_id": FISH_AUDIO_MODEL_ID,
        "format": "mp3",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:

            if response.status != 200:
                error = await response.text()
                raise Exception(
                    f"Fish Audio 오류 {response.status}: {error}"
                )

            audio_data = await response.read()

    temp = tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    )

    temp.write(audio_data)
    temp.close()

    return temp.name


@bot.command()
async def 핑(ctx):
    await ctx.send("퐁! 🏓")


@bot.command()
async def 말(ctx, *, text):

    if not ctx.author.voice:
        await ctx.send("먼저 음성채널에 들어가줘!")
        return

    voice_channel = ctx.author.voice.channel

    try:

        if ctx.voice_client is None:
            voice_client = await voice_channel.connect()

        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        else:
            voice_client = ctx.voice_client

        await ctx.send(f"🔊 말하는 중: {text}")

        async with tts_lock:

            audio_file = await make_tts(text)

            while voice_client.is_playing():
                await asyncio.sleep(0.2)

            audio_source = discord.FFmpegPCMAudio(audio_file)

            voice_client.play(audio_source)

            while voice_client.is_playing():
                await asyncio.sleep(0.2)

        os.remove(audio_file)

    except Exception as e:

        print(f"TTS 오류: {e}")

        await ctx.send("❌ TTS 재생 중 오류가 발생했어.")

        
@bot.command()
async def 퇴장(ctx):

    if ctx.voice_client:

        await ctx.voice_client.disconnect()

        await ctx.send("👋 음성채널에서 나갔어!")

    else:

        await ctx.send("나는 지금 음성채널에 없어.")


bot.run(DISCORD_TOKEN)
