import os
import random
import discord
from discord.ext import commands
import emoji
import re

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


# =========================
# 打開垃圾桶（占卜）
# =========================

@bot.tree.command(name="打開垃圾桶", description="打開垃圾桶看看裡面有什麼")
async def divination(interaction: discord.Interaction):
    filtered = []

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
        # 1) 由兩個 Regional Indicator 組成的國旗（🇹🇼 這種）
        cps = [ord(c) for c in ch]
        regional = [cp for cp in cps if 0x1F1E6 <= cp <= 0x1F1FF]
        if len(regional) >= 2:
            return True

        # 2) Tag sequence flags（🏴 這種，像英格蘭/蘇格蘭/威爾斯）
        if cps and cps[0] == 0x1F3F4:
            return True

        return False

    for e, data in emoji.EMOJI_DATA.items():
        # 你裝的 emoji 版本可能沒有 group/category，所以要做 fallback
        group = data.get("group") or data.get("category")  # 可能是 None
        name = (data.get("en") or "").lower()

        # ✅ 若 group/category 存在才做分類限制；不存在就不靠分類過濾（避免全清空）
        if group and group not in allowed_groups:
            continue

        # ✅ 國旗：兩層保險
        if is_flag_emoji(e):
            continue
        # 有些版本 name 會是 "flag: ..." 或 demojize 才看得出來
        if "flag" in name or emoji.demojize(e).lower().startswith(":flag_"):
            continue

        # 排除完整人物（但保留手勢 / 身體部位）
        if group == "People & Body" or (not group):  # 沒 group 時也照樣用關鍵字擋人類
            if any(word in name for word in [
                "man", "woman", "boy", "girl", "person",
                "people", "family", "pregnant",
                "bride", "groom", "prince", "princess",
                "superhero", "supervillain"
            ]):
                continue

        filtered.append(e)

    if not filtered:
        await interaction.response.send_message(
            "沒有可用 emoji（可能是 emoji 套件版本沒有 group/category，或過濾太嚴格）。"
        )
        return

    pick = random.choice(filtered)
    await interaction.response.send_message(f"打開垃圾桶看到裡面有 {pick}")


# =========================
# 二選一
# =========================

@bot.tree.command(name="二選一", description="給兩個選項，我幫你選一個")
async def choose_one(interaction: discord.Interaction, 選項一: str, 選項二: str):
    pick = random.choice([選項一, 選項二])
    await interaction.response.send_message(f"我選：{pick}")


# =========================
# 骰子
# =========================

@bot.tree.command(name="骰子", description="TRPG 骰子：例如 1d100、2d6+3、d20-1")
async def roll_dice(interaction: discord.Interaction, 骰子: str):
    s = 骰子.strip().lower().replace(" ", "")

    # 支援格式：1d100、d20、2d6+3、d20-1
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

    # 防止爆炸
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

if __name__ == "__main__":
    bot.run(TOKEN)
