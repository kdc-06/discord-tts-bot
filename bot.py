import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"봇 로그인 성공: {bot.user}")
    print("TTS 봇이 준비되었습니다.")


@bot.command()
async def 핑(ctx):
    await ctx.send("퐁! 🏓")


@bot.command()
async def 말(ctx, *, text):
    await ctx.send(f"🔊 TTS 요청: {text}")


@bot.command()
async def 퇴장(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("음성채널에서 나갔어요.")
    else:
        await ctx.send("현재 음성채널에 들어가 있지 않아요.")


bot.run(TOKEN)
