@bot.tree.command(name="占卜", description="打開垃圾桶看看裡面有什麼")
async def divination(interaction: discord.Interaction):

    filtered = []

    for e, data in emoji.EMOJI_DATA.items():
        name = data.get("en", "")

        # 排除人類 / 角色 / 家庭 / 職業 / 國旗
        if any(word in name for word in [
            "man", "woman", "person",
            "boy", "girl", "family",
            "pregnant", "bride", "groom",
            "vampire", "mage", "elf",
            "fairy", "zombie",
            "prince", "princess",
            "superhero", "supervillain",
            "flag"
        ]):
            continue

        filtered.append(e)

    if not filtered:
        await interaction.response.send_message("垃圾桶是空的…")
        return

    pick = random.choice(filtered)

    await interaction.response.send_message(
        f"打開垃圾桶看到了裡面有{pick}"
    )
