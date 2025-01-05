import discord  # Library to interact with Discord servers, users, and messages.
from discord.ext import commands  # Framework for creating and managing bot commands.
import os  # Allows access to environment variables and file system operations.
from dotenv import load_dotenv  # Loads environment variables from a ".env" file.

# Load environment variables from .env file
# (e.g., your bot token and the channel ID where the bot will operate)
load_dotenv()

# Retrieve the bot's token from the .env file (used to log in the bot)
TOKEN = os.getenv('DISCORD_TOKEN')

# Retrieve the target channel ID from the .env file (the bot will operate in this channel)
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))

# Set up the bot's "intents," which define what kind of events the bot is allowed to interact with
# `message_content` and `messages` are required to allow the bot to read messages in a channel
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Create a bot instance, with the prefix "!" for its commands (e.g., "!command")
bot = commands.Bot(command_prefix="!", intents=intents)

# Event triggered when the bot is ready and connected to Discord servers
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}.")  # Print confirmation the bot is online

    # Look for Python files (cogs) in the "cogs" folder and load them
    for filename in os.listdir("./cogs"):
        # Only load files that end with ".py" (ignore other file types)
        if filename.endswith(".py"):
            # Load the cog dynamically, using its file name without the ".py" extension
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded cog {filename[:-3]}")  # Confirm each cog is loaded

# Run the bot using the token from the .env file
# This starts the bot and connects it to Discord
bot.run(TOKEN)