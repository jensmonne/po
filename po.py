# Import required modules
import discord  # The Discord library for building bots
import os  # Provides a way to access environment variables
import json  # Allows reading and writing JSON (data storage format)
from dotenv import load_dotenv  # Helps load environment variables from the .env file

# Load environment variables from the .env file
load_dotenv()

# Retrieve the bot's token from the environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Retrieve the ID of the channel where the bot will operate
TARGET_CHANNEL_ID = os.getenv('TARGET_CHANNEL_ID')

# File name to store the "po" counts for each users
PO_COUNTS_FILE = 'po_counts.json'

# Initialize the bot with the necessary permissions (intents)
intents = discord.Intents.default()
intents.message_content = True  # Allow the bot to access message content
intents.messages = True  # Allow the bot to access messages
client = discord.Client(intents=intents)

# Function to load "po" counts from the JSON file
def load_po_counts():
    if os.path.exists(PO_COUNTS_FILE):  # Check if the file exists
        try:
            with open(PO_COUNTS_FILE, 'r') as file:  # Open the file in read mode
                return json.load(file)  # Load the JSON data as a Python dictionary
        except (json.JSONDecodeError, IOError):
            # If the file is invalid or unreadable, reset the data
            print(f"Warning: '{PO_COUNTS_FILE}' is empty or corrupted. Resetting data.")
            return {}
    return {}  # Return an empty dictionary if the file doesn't exist

# Function to save "po" counts back to the JSON file
def save_po_counts():
    with open(PO_COUNTS_FILE, 'w') as file:  # Open the file in write mode
        json.dump(po_counts, file)  # Save the current data to the file

# Dictionary to store the "po count" for each user
po_counts = load_po_counts()

# Function to recount all messages containing "po" in the target channel
async def recount_po_messages(channel):
    """Recount all messages containing 'po' in the channel."""
    global po_counts
    po_counts = {}  # Reset the counts
    async for message in channel.history(limit=None):  # Loop through all messages in the channel
        # Ignore messages sent by the bot or messages starting with '!'
        if message.author == client.user or message.content.startswith('!'):
            continue

        # Check if the message contains the word "po" (not case-sensitive)
        if 'po' in message.content.lower():
            user_id = str(message.author.id)  # Get the user's ID
            po_counts[user_id] = po_counts.get(user_id, 0) + 1  # Increment the user's count

    save_po_counts()  # Save the updated counts to the file

# Event: Triggered when the bot is ready to operate
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')  # Log that the bot is online

    # Find the target channel using its ID
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if channel:
        print("Recounting messages in the target channel...")
        await recount_po_messages(channel)  # Recount "po" messages in the channel
        print("Recount complete.")
    else:
        print(f"Error: Channel with ID {TARGET_CHANNEL_ID} not found.")

# Event: Triggered whenever a message is sent in a server
@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Ignore messages not sent in the target channel
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    user_id = str(message.author.id)  # Convert user ID to a string for storage in JSON

    # Handle commands (messages starting with '!')
    if message.content.startswith('!'):

        # Handle the "!po" command
        if message.content == "!po":
            current_count = po_counts.get(user_id, 0)  # Get the user's count (or 0 if not found)
            await message.channel.send(f'{message.author.mention}, your current po count is {current_count}.')
            return

        # Handle the "!pol" or "!poleaderboard" commands
        if message.content.startswith('!pol') or message.content.startswith('!poleaderboard'):
            sorted_counts = sorted(po_counts.items(), key=lambda x: x[1], reverse=True)  # Sort by count, descending

            # Build the leaderboard text
            leaderboard = "**Po Leaderboard**\n"
            for rank, (user, count) in enumerate(sorted_counts[:3], start=1):  # Top 3 users
                try:
                    member = await message.guild.fetch_member(int(user))  # Get user details
                    username = member.name  # Get the user's name
                except discord.NotFound:
                    username = f"Unknown User ({user})"  # Handle cases where the user is no longer in the server

                leaderboard += f"#{rank}: {username} with {count} po(s)\n"

            # Find the rank and count of the current user
            user_rank = next((i + 1 for i, (u, _) in enumerate(sorted_counts) if u == user_id), None)
            user_po_count = po_counts.get(user_id, 0)

            # Add the user's rank and count to the leaderboard
            if user_rank:
                leaderboard += f"\nYour rank: #{user_rank} with {user_po_count} po(s)."
            else:
                leaderboard += f"\nYou are not on the leaderboard yet. You have {user_po_count} po(s)."

            await message.channel.send(leaderboard)  # Send the leaderboard
            return

    # Handle messages containing the word "po"
    else:
        if 'po' in message.content.lower():
            current_count = po_counts.get(user_id, 0)  # Get the user's current count
            po_counts[user_id] = current_count + 1  # Increment the count
            save_po_counts()  # Save the updated count to the file

# Run the bot using the token from the environment variables
client.run(TOKEN)