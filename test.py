@client.tree.command(name="test", description="test description")
@app_commands.describe(testin = "test input")
async def test(interaction: discord.Interaction, testin: str):

    await interaction.response.defer()
    await asyncio.sleep(1)

    datetime = await get_time()
    datetime = datetime.replace(" ", "")
    datetime = datetime.replace(":", "")

    try:
        f = open(r"path\to\file.txt", "r")
        msg = f.read()
        file=discord.File(r"path\to\file.png", filename="image.png")
        embed = discord.Embed(title="", description=f"{interaction.user.mention}\n" + msg,colour=discord.Color.from_rgb(25, 25, 26))
        embed.set_image(url="attachment://image.png")
        await interaction.followup.send(file=file,embed=embed)
    except Exception as exc:
        print(exc)