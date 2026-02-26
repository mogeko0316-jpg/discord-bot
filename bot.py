import os
import random
import discord
from discord.ext import commands
import emoji

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("找不到 DISCORD_TOKEN 環境變數")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"已同步 {len(synced)} 個指令")
    print("機器人已上線")

@bot.tree.command(name="占卜", description="打開垃圾桶看看裡面有什麼")
async def divination(interaction: discord.Interaction):

    allowed_groups = {
        "Smileys & Emotion",   # 表情 / 臉
        "People & Body",       # 手勢 / 身體部位
        "Animals & Nature",    # 自然
        "Food & Drink",        # 食物
        "Activities",          # 活動
        "Objects",             # 物品
        "Symbols"              # 符號
    }

    filtered = []

    for e, data in emoji.EMOJI_DATA.items():
        group = data.get("group")

        # 只保留你指定的分類
        if group in allowed_groups:

            name = data.get("en", "")

            # 排除單人、職業、家庭、角色
            if any(word in name for word in [
                "man", "woman", "person",
                "boy", "girl", "family",
                "pregnant", "bride", "groom",
                "vampire", "mage", "elf",
                "fairy", "zombie"
            ]):
                continue

            filtered.append(e)

    pick = random.choice(filtered)

    await interaction.response.send_message(
        f"打開垃圾桶看到了裡面有{pick}"
    )

if __name__ == "__main__":
    bot.run(TOKEN)
