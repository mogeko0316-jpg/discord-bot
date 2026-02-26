import os
import random
import discord
from discord.ext import commands
import emoji

# 從環境變數讀取 Token（Railway 變數名稱要叫 DISCORD_TOKEN）
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
    filtered = []

    # 你不想要：人類/身分/家庭/職業/多人 + 國旗
    ban_words = {
        # 人類/多人/家庭
        "person", "people", "man", "woman", "boy", "girl", "family",

        # 身分（孕婦/婚禮）
        "pregnant", "bride", "groom",

        # 常見職業/身分
        "police", "cop", "detective", "guard",
        "pilot", "chef", "cook", "judge",
        "farmer", "student", "teacher",
        "doctor", "nurse", "worker",

        # 角色類（避免人物類延伸）
        "superhero", "supervillain",
        "prince", "princess",

        # 國旗
        "flag",
    }

    for e, data in emoji.EMOJI_DATA.items():
        name = (data.get("en") or "").lower()

        # 依名稱關鍵字排除
        if any(w in name for w in ban_words):
            continue

        filtered.append(e)

    # ✅ 防呆：避免 filtered 被你刪到 0 個導致 random.choice 爆炸
    if not filtered:
        await interaction.response.send_message("你把 emoji 刪到剩 0 個了（過濾太嚴格）。請放寬 ban_words。")
        return

    pick = random.choice(filtered)
    await interaction.response.send_message(f"打開垃圾桶看到裡面有 {pick}")

if __name__ == "__main__":
    bot.run(TOKEN)
