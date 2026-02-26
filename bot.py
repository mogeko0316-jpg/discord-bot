import os
import random
import discord
from discord.ext import commands
import emoji
import re

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("找不到 DISCORD_TOKEN 環境變數")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"已同步 {len(synced)} 個指令：{[c.name for c in synced]}")
    except Exception as e:
        print("同步失敗：", repr(e))
    print("機器人已上線")


# =========================
# 共用：抽垃圾桶 emoji
# =========================

allowed_groups = {
    "Smileys & Emotion",   # 表情
    "People & Body",       # 手勢 / 身體部位
    "Animals & Nature",    # 動物 / 自然
    "Food & Drink",        # 食物 / 飲料
    "Activities",          # 活動 / 運動
    "Travel & Places",     # 交通工具
    "Objects",             # 物品
}

def is_flag_emoji(ch: str) -> bool:
    cps = [ord(c) for c in ch]

    # 1) Regional Indicator flags (🇹🇼)
    regional = [cp for cp in cps if 0x1F1E6 <= cp <= 0x1F1FF]
    if len(regional) >= 2:
        return True

    # 2) Tag-sequence flags (🏴 + tags)
    if cps and cps[0] == 0x1F3F4:
        return True

    return False

def pick_trash_emoji() -> str | None:
    filtered = []

    for e, data in emoji.EMOJI_DATA.items():
        group = data.get("group") or data.get("category")  # 有些版本用 category
        name = (data.get("en") or "").lower()

        # 若有 group/category 才做白名單；沒有就不靠分類（避免全清空）
        if group and group not in allowed_groups:
            continue

        # 國旗排除（最可靠）
        if is_flag_emoji(e):
            continue
        # 英文名稱也擋掉旗幟
        if "flag" in name:
            continue

        # People & Body：排除人物，只留手勢/部位
        if group == "People & Body":
            if any(word in name for word in [
                "man", "woman", "boy", "girl", "person",
                "people", "family", "pregnant",
                "bride", "groom", "prince", "princess",
                "superhero", "supervillain"
            ]):
                continue

        filtered.append(e)

    if not filtered:
        return None

    return random.choice(filtered)


# =========================
# Slash：打開垃圾桶
# =========================

@bot.tree.command(name="打開垃圾桶", description="打開垃圾桶看看裡面有什麼")
async def divination(interaction: discord.Interaction):
    pick = pick_trash_emoji()
    if not pick:
        await interaction.response.send_message("沒有可用 emoji（可能是 emoji 套件資料不完整或過濾太嚴格）。")
        return
    await interaction.response.send_message(f"打開垃圾桶看到裡面有 {pick}")


# =========================
# Slash：二選一
# =========================

@bot.tree.command(name="二選一", description="給兩個選項，我幫你選一個")
async def choose_one(interaction: discord.Interaction, 選項一: str, 選項二: str):
    pick = random.choice([選項一, 選項二])
    await interaction.response.send_message(f"我選：{pick}")


# =========================
# Slash：骰子
# =========================

@bot.tree.command(name="骰子", description="TRPG 骰子：例如 1d100、2d6+3、d20-1")
async def roll_dice(interaction: discord.Interaction, 骰子: str):
    s = 骰子.strip().lower().replace(" ", "")
    m = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", s)
    if not m:
        await interaction.response.send_message("格式錯誤：請用像 1d100、d20、2d6+3、d20-1")
        return

    n_str, sides_str, mod_str = m.groups()
    n = int(n_str) if n_str else 1
    sides = int(sides_str)
    mod = int(mod_str) if mod_str else 0

    if n <= 0 or sides <= 0:
        await interaction.response.send_message("數字要是正整數")
        return
    if n > 200:
        await interaction.response.send_message("骰子顆數太多了（上限 200）")
        return

    rolls = [random.randint(1, sides) for _ in range(n)]
    total = sum(rolls) + mod
    detail = "+".join(map(str, rolls))
    mod_text = f"{mod:+d}" if mod != 0 else ""

    await interaction.response.send_message(
        f"🎲 {n}d{sides}{mod_text}\n"
        f"結果：{detail}{mod_text} = **{total}**"
    )


# =========================
# 文字觸發（非 slash）
# =========================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    txt = message.content.strip()

    # 直接打：打開垃圾桶
    if txt == "打開垃圾桶":
        pick = pick_trash_emoji()
        if not pick:
            await message.channel.send("沒有可用 emoji（可能是 emoji 套件資料不完整或過濾太嚴格）。")
        else:
            await message.channel.send(f"打開垃圾桶看到裡面有 {pick}")
        return

    # 直接打：二選一 A | B
    if txt.startswith("二選一"):
        parts = txt[3:].split("|")
        if len(parts) == 2:
            a = parts[0].strip()
            b = parts[1].strip()
            if a and b:
                await message.channel.send(f"我選：{random.choice([a, b])}")
                return

    # 直接打：1d100 / d20 / 2d6+3
    m = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", txt.lower().replace(" ", ""))
    if m:
        n_str, sides_str, mod_str = m.groups()
        n = int(n_str) if n_str else 1
        sides = int(sides_str)
        mod = int(mod_str) if mod_str else 0
        if 1 <= n <= 200 and sides > 0:
            rolls = [random.randint(1, sides) for _ in range(n)]
            total = sum(rolls) + mod
            detail = "+".join(map(str, rolls))
            mod_text = f"{mod:+d}" if mod != 0 else ""
            await message.channel.send(f"🎲 {n}d{sides}{mod_text}\n結果：{detail}{mod_text} = **{total}**")
            return

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(TOKEN)
