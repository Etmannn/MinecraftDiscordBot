# Minecraft Discord Bot by Ethan Cleminson | 10/2/2024

# Packages used in program
import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
import yaml
import asyncio

# Open and read config file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# constants
server = JavaServer.lookup(f"127.0.0.1:{config['port']}")

# Set discord bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
bot.remove_command("help")

# Pings server to check if its online
def serverping():
    try:
        server.ping()
    except (TimeoutError, OSError):
        return False
    else:
        return True

@tasks.loop(seconds=5)
async def auto_stop():
    online = serverping()
    if online == True and server.status().players.online == 0:
        await asyncio.sleep(config['time'])
        if online == True and server.status().players.online == 0:
            await asyncio.create_subprocess_shell("TASKKILL /F /IM java.exe")
            if config['playit'] == 'true':
                await asyncio.create_subprocess_shell("TASKKILL /F /IM playit.exe")

# Prints a message and sets activitiy to the help command; triggers when the bot is online
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="/help")
    )
    await bot.tree.sync()
    channel = bot.get_channel(config['channel'])
    await channel.send("Bot Successfully Logged on!")
    print("Bot successfully logged on!")
    auto_stop.start()

# A command to check if the server is online
@bot.tree.command(name="ping", description="Checks Server Status")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Checking...")
    online = serverping()
    if online is True:
        await interaction.followup.send(f"Server is Online! There are currently {server.status().players.online} players online.")
    if online is False:
        await interaction.followup.send("Server is Offline")

# A command to start the Minecraft server
# If the server is already online it will inform the user
@bot.tree.command(name="start", description="Starts the Minecraft server")
async def start(interaction: discord.Interaction):
    online = serverping()
    if online is True:
        await interaction.response.send_message("Server already Online")
    else:
        await interaction.response.send_message("Server is starting!")
        await asyncio.create_subprocess_shell(f"start cmd.exe /c {config['startbat']}", shell=True)
        if config['playit'] == 'true':
            await asyncio.create_subprocess_shell("TASKKILL /F /IM playit.exe")
            await asyncio.create_subprocess_shell('start cmd.exe /c playit.exe', shell=True)
        checking = True
        while checking is True:
            checkstat = serverping()
            if checkstat is True:
                await interaction.followup.send(f"Server Online! The server will automatically stop in {config['time']} seconds.")
                checking = False

# A command to stop the Minecraft server
# If the server is not online it will inform the user
@bot.tree.command(name="stop", description="Stops the Minecraft server")
async def stop(interaction: discord.Interaction):
    online = serverping()
    if online is True:
        await asyncio.create_subprocess_shell("TASKKILL /F /IM java.exe")
        if config['playit'] == 'true':
            await asyncio.create_subprocess_shell("TASKKILL /F /IM playit.exe")
        await interaction.response.send_message("Server Offline")
    else:
        await interaction.response.send_message("Sever already Offline")

# A command to restart the Minecraft server
@bot.tree.command(name="restart", description="Restarts the Minecraft server")
async def restart(interaction: discord.Interaction):
    online = serverping()
    if online is True:
        await interaction.response.send_message("Server Restarting...")
        await asyncio.create_subprocess_shell("TASKKILL /F /IM java.exe")
        if config['playit'] == 'true':
            await asyncio.create_subprocess_shell("TASKKILL /F /IM playit.exe")
        await interaction.followup.send("Server Offline")

        await interaction.followup.send("Server is starting!")
        await asyncio.create_subprocess_shell(f"start cmd.exe /c {config['startbat']}", shell=True)
        if config['playit'] == 'true':
            await asyncio.create_subprocess_shell("TASKKILL /F /IM playit.exe")
            await asyncio.create_subprocess_shell('start cmd.exe /c playit.exe', shell=True)
        checking = True
        while checking is True:
            checkstat = serverping()
            if checkstat is True:
                await interaction.followup.send(
                    f"Server Online! The server will automatically stop in {config['time']} seconds.")
                checking = False
    else:
        await interaction.response.send_message("Server Offline")


# Displays all the commands of the bot in a discord embed
@bot.tree.command(name="help")
async def help(interaction: discord.Interaction):
    helpembed = discord.Embed(title="Commands", color=0x55FF55)

    helpembed.add_field(name="/ping", value="Checks Server Status", inline=False)
    helpembed.add_field(
        name="/start", value="Starts the Minecraft server", inline=False
    )
    helpembed.add_field(
        name="/stop", value="Stops the Minecraft server", inline=False
    )
    helpembed.add_field(
        name="/restart", value="Restarts the Minecraft server", inline=False
    )
    await interaction.response.send_message(embed=helpembed)

# Runs the bot using the bot token
bot.run(config['token'])