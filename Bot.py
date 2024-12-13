# Minecraft Discord Bot by Ethan Cleminson | 10/2/2024
# Packages used in program

import discord
from discord.ext import commands
import subprocess
from mcstatus import JavaServer
import yaml

# Open and read config file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# constants
server = JavaServer.lookup(config['ip'])

# Set discord bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)
bot.remove_command("help")

# Pings server to check if its online
def serverping():
    try:
        server.ping()
    except (TimeoutError, OSError):
        return False
    else:
        return True

# Prints a message and sets activitiy to the help command; triggers when the bot is online
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=f"{config['prefix']}help")
    )

    global channel
    channel = bot.get_channel(config['channel'])

    await channel.send("Bot Successfully Logged on!")


# A command to check if the server is online
@bot.command()
@commands.has_role(config['ping'])
async def ping(ctx):
    online = serverping()
    if online is True:
        await channel.send(f"Server is Online! There are currently {server.status().players.online} players online.")
    if online is False:
        await channel.send("Server is Offline")

# A command to start the Minecraft server
# If the server is already online it will inform the user
@bot.command()
@commands.has_role(config['start'])
async def start(ctx):
    online = serverping()
    if online is True:
        await channel.send("Server already Online")
    else:
        await channel.send("Server is starting!")
        subprocess.Popen(config['serverdir'])
        checking = True
        while checking is True:
            checkstat = serverping()
            if checkstat is True:
                await channel.send("Server Online!")
                checking = False

# A command to stop the Minecraft server
# If the server is not online it will inform the user
@bot.command()
@commands.has_role(config['stop'])
async def stop(ctx):
    online = serverping()
    if online is True:
        subprocess.call("TASKKILL /F /IM java.exe", shell=True)
        if config['playit'] == 'true':
            subprocess.call("TASKKILL /F /IM playit.exe", shell=True)
        await channel.send("Server Offline")
    else:
        await channel.send("Sever already Offline")

# A command to restart the Minecraft server
@bot.command()
@commands.has_role(config['restart'])
async def restart(ctx):
    online = serverping()
    if online is True:
        await stop(ctx)
        await start(ctx)
    else:
        await channel.send("Server Offline")


# Displays all the commands of the bot in a discord embed
@bot.command()
@commands.has_role(config['help'])
async def help(ctx):
    helpembed = discord.Embed(title="Commands", color=0x55FF55)

    helpembed.add_field(name="mc!ping", value="Checks Server Status", inline=False)
    helpembed.add_field(
        name="mc!start", value="Starts the minecraft server", inline=False
    )
    helpembed.add_field(
        name="mc!stop", value="Stops the minecraft server", inline=False
    )
    helpembed.add_field(
        name="mc!restart", value="Restarts the minecraft server", inline=False
    )
    await channel.send(embed=helpembed)

# Runs the bot using the bot token
bot.run(config['token'])
