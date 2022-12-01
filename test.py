# create new command
@client.tree.command(name="test", description="test description")
# if command has input
@app_commands.describe(test_input = "test input")
# the command is like a method that takes input and it's type
async def test(interaction: discord.Interaction, test_input: str):

    # defer the response while bot processes the command
    await interaction.response.defer()
    await asyncio.sleep(1)

    # if time is needed
    datetime = await get_time()
    datetime = datetime.replace(" ", "")
    datetime = datetime.replace(":", "")

    try:
        # open text file if necessary
        f = open(r"path\to\file.txt", "r")
        # read from the file
        msg = f.read()
        # set image ot txt file as attachment in the embed
        file=discord.File(r"path\to\file.png", filename="image.png")
        # set the embed's title and description and the message string
        embed = discord.Embed(title="", description=f"{interaction.user.mention}\n" + msg,colour=discord.Color.from_rgb(25, 25, 26))
        # set the embed's image from attachment
        embed.set_image(url="attachment://image.png")
        # send the response
        await interaction.followup.send(file=file,embed=embed)
    except Exception as exc:
        print(exc)
        # set the error message
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        # set the embed message
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        # send the response
        await interaction.followup.send(embed=embed)
        print(exc)
        # log exception
        exc(interaction, "/command" + command_input, exc)
