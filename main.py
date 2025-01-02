import discord
import os
import json
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve your bot token from the environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# The ID of the channel where the bot should operate
TARGET_CHANNEL_ID = 1324509748003078248

# File to store the po counts
PO_COUNTS_FILE = 'po_counts.json'

# Initialize the bot with proper intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Load po counts from the JSON file
def load_po_counts():
    if os.path.exists(PO_COUNTS_FILE):
        try:
            with open(PO_COUNTS_FILE, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            # Return an empty dictionary if the file is invalid or unreadable
            print(f"Warning: '{PO_COUNTS_FILE}' is empty or corrupted. Resetting data.")
            return {}
    return {}

# Save po counts to the JSON file
def save_po_counts():
    with open(PO_COUNTS_FILE, 'w') as file:
        json.dump(po_counts, file)

# Dictionary to store the "po count" for each user
po_counts = load_po_counts()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message is in the target channel
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    user_id = str(message.author.id)  # Store user_id as string for JSON compatibility

    # Respond to the !po command
    if message.content.startswith('!po'):
        # Get the current count or default to 0 if not found
        current_count = po_counts.get(user_id, 0)

        # Respond with the current po count
        await message.channel.send(f'{message.author.mention}, your current po count is {current_count}.')
        return
    
    # Check if the message contains the word "po" (case-insensitive)
    if 'po' in message.content.lower():
        # Get the current count or default to 0 if not found
        current_count = po_counts.get(user_id, 0)

        # Update the po count for the user
        po_counts[user_id] = current_count + 1
        save_po_counts()

# Run the bot
client.run(TOKEN)