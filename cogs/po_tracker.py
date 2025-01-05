import discord  # Library to interact with Discord servers, users, and messages.
from discord.ext import commands  # Framework for creating and managing bot commands.
import re  # Provides tools for working with regular expressions (used to match patterns in text).
import json  # Used to read and write JSON files (to store user data).
import os  # Allows access to environment variables and file system operations.

# Regular expression pattern to match the word 'po' as a standalone word, case-insensitive
PO_PATTERN = re.compile(r'\bpo\b', re.IGNORECASE)

# File name to store "po" counts for each user
PO_COUNTS_FILE = 'po_counts.json'

# Target channel ID where the bot operates, retrieved from environment variables
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))

# Function to load "po" counts from a JSON file
def load_po_counts():
    if os.path.exists(PO_COUNTS_FILE):  # Check if the file exists
        try:
            with open(PO_COUNTS_FILE, 'r') as file:
                return json.load(file)  # Load and return the data as a dictionary
        except (json.JSONDecodeError, IOError):
            # If the file is invalid or unreadable, warn and return an empty dictionary
            print(f"Warning: '{PO_COUNTS_FILE}' is empty or corrupted. Resetting data.")
            return {}
    return {}  # If the file doesn't exist, return an empty dictionary

# Function to save "po" counts back to the JSON file
def save_po_counts(po_counts):
    with open(PO_COUNTS_FILE, 'w') as file:
        json.dump(po_counts, file)  # Write the current data to the file

# Define the PoTracker cog (a module that adds specific functionality to the bot)
class PoTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Reference to the bot instance
        self.po_counts = load_po_counts()  # Load "po" counts from the file when the bot starts

    # Event listener: Triggered when a new message is sent in a server
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages not sent in the target channel
        if message.channel.id != TARGET_CHANNEL_ID:
            return

        # Ignore messages sent by bots (including this bot)
        if message.author.bot:
            return

        # Check if the message contains the word 'po'
        if PO_PATTERN.search(message.content):
            user_id = str(message.author.id)  # Convert the author's ID to string for JSON compatibility
            self.po_counts[user_id] = self.po_counts.get(user_id, 0) + 1  # Increment the user's "po" count
            save_po_counts(self.po_counts)  # Save updated counts to the file

    # Command: Show the "po" count for the user or a mentioned user
    @commands.command(name="po")
    async def show_po_count(self, ctx):
        # Check if a user was mentioned in the command
        if ctx.message.mentions:
            mentioned_user = ctx.message.mentions[0]  # Get the first mentioned user
            user_id = str(mentioned_user.id)  # Convert their ID to string for lookup
            count = self.po_counts.get(user_id, 0)  # Get their "po" count
            await ctx.send(f"{mentioned_user} has a po count of {count}.")  # Send the count to the channel
        else:
            # If no user is mentioned, show the command issuer's "po" count
            user_id = str(ctx.author.id)
            count = self.po_counts.get(user_id, 0)
            await ctx.send(f"{ctx.author.mention}, your current po count is {count}.")  # Send the count to the channel

# Function to set up the cog (called when the bot loads this cog)
async def setup(bot):
    await bot.add_cog(PoTracker(bot))  # Add the cog to the bot