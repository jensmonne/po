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
intents.messages = True
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

async def recount_po_messages(channel):
    """Recount all messages containing 'po' in the channel."""
    global po_counts
    po_counts = {}  # Reset the counts
    async for message in channel.history(limit=None):
        # Ignore messages from the bot and messages starting with '!'
        if message.author == client.user or message.content.startswith('!'):
            continue

        # Check if the message contains the word 'po' (case-insensitive)
        if 'po' in message.content.lower():
            user_id = str(message.author.id)
            po_counts[user_id] = po_counts.get(user_id, 0) + 1

    save_po_counts()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    # Get the target channel
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if channel:
        print("Recounting messages in the target channel...")
        await recount_po_messages(channel)
        print("Recount complete.")
    else:
        print(f"Error: Channel with ID {TARGET_CHANNEL_ID} not found.")

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message is in the target channel
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    user_id = str(message.author.id)  # Store user_id as string for JSON compatibility

    if message.content.startswith('!'):

        # Respond to the !po command
        if message.content == "!po":
            # Get the current count or default to 0 if not found
            current_count = po_counts.get(user_id, 0)

            # Respond with the current po count
            await message.channel.send(f'{message.author.mention}, your current po count is {current_count}.')
            return

        # Respond to the !pol or !poleaderboard commands
        if message.content.startswith('!pol') or message.content.startswith('!poleaderboard'):
            # Sort users by their po counts in descending order
            sorted_counts = sorted(po_counts.items(), key=lambda x: x[1], reverse=True)

            # Generate the leaderboard text for the top 3 users
            leaderboard = "**Po Leaderboard**\n"
            for rank, (user, count) in enumerate(sorted_counts[:3], start=1):
                try:
                    member = await message.guild.fetch_member(int(user))
                    username = member.name
                except discord.NotFound:
                    username = f"Unknown User ({user})"
                
                leaderboard += f"#{rank}: {username} with {count} po(s)\n"

            # Find the rank of the current user
            user_rank = next((i + 1 for i, (u, _) in enumerate(sorted_counts) if u == user_id), None)
            user_po_count = po_counts.get(user_id, 0)

            # Add the user's rank to the message
            if user_rank:
                leaderboard += f"\nYour rank: #{user_rank} with {user_po_count} po(s)."
            else:
                leaderboard += f"\nYou are not on the leaderboard yet. You have {user_po_count} po(s)."

            # Send the leaderboard message
            await message.channel.send(leaderboard)
            return
    else:

        # Check if the message contains the word "po" (case-insensitive)
        if 'po' in message.content.lower():
            # Get the current count or default to 0 if not found
            current_count = po_counts.get(user_id, 0)

            # Update the po count for the user
            po_counts[user_id] = current_count + 1
            save_po_counts()

# Run the bot
client.run(TOKEN)