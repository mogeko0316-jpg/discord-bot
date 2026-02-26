import os
import random
import discord
from discord.ext import commands
import emoji

# 從雲端環境變數讀取 Token
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("找不到 DISCORD_TOKEN 環境變數")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"已同步 {len(synced)} 個指令：{[c.name for c in synced]}")
    except Exception as e:
        print("同步失敗：", repr(e))
    print("機器人已上線")

@bot.tree.command(name="占卜", description="打開垃圾桶看看裡面有什麼")
async def divination(interaction: discord.Interaction):

    # 抓所有 Unicode emoji
    all_emojis = list(emoji.EMOJI_DATA.keys())

    # 排除人類相關
    filtered = []
    for e in all_emojis:
        name = emoji.EMOJI_DATA[e]["en"]
        if any(word in name for word in [
            "person", "man", "woman", "boy", "girl",
            "family", "skin tone"
        ]):
            continue
        filtered.append(e)

    pick = random.choice(filtered)

    await interaction.response.send_message(
        f"打開垃圾桶看到了裡面有{pick}"
    )

if __name__ == "__main__":
    bot.run(TOKEN)