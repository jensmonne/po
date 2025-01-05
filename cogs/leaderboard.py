import discord  # Library to interact with Discord servers, users, and messages.
from discord.ext import commands  # Framework for creating and managing bot commands.
import json  # Used to read and write JSON files (to store user data).
import os  # Allows access to environment variables and file system operations.

# File name where the "po" counts for users are stored
PO_COUNTS_FILE = 'po_counts.json'

# Function to load "po" counts from the JSON file
def load_po_counts():
    if os.path.exists(PO_COUNTS_FILE):  # Check if the file exists
        try:
            with open(PO_COUNTS_FILE, 'r') as file:
                return json.load(file)  # Load and return the data as a dictionary
        except (json.JSONDecodeError, IOError):
            # If the file is invalid or unreadable, return an empty dictionary
            return {}
    return {}  # Return an empty dictionary if the file doesn't exist

# Define the Leaderboard cog (a module to handle leaderboard functionality)
class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Reference to the bot instance

    # Command: Show the leaderboard for top "po" counts
    @commands.command(name="pol", aliases=["poleaderboard"])
    async def show_leaderboard(self, ctx, count: int = 3):
        # Ensure the requested count is between 1 and 25
        count = min(max(count, 1), 25)

        # Load the "po" counts from the file
        po_counts = load_po_counts()

        # Sort the counts in descending order
        sorted_counts = sorted(po_counts.items(), key=lambda x: x[1], reverse=True)

        # Create the leaderboard string
        leaderboard = f"**Po Leaderboard (Top {count})**\n"
        for rank, (user, user_count) in enumerate(sorted_counts[:count], start=1):
            # Attempt to get the member's name from the server cache or fetch it
            member = ctx.guild.get_member(int(user))
            if member is None:
                member = await ctx.guild.fetch_member(int(user))  # Fallback if not in cache
            username = member.name if member else f"Unknown User ({user})"  # Handle unknown users
            leaderboard += f"#{rank}: {username} with {user_count} po(s)\n"

        # Get the rank and count of the user who invoked the command
        user_id = str(ctx.author.id)
        user_rank = next((i + 1 for i, (u, _) in enumerate(sorted_counts) if u == user_id), None)
        user_po_count = po_counts.get(user_id, 0)

        # Add the user's rank and count to the leaderboard message
        if user_rank:
            leaderboard += f"\nYour rank: #{user_rank} with {user_po_count} po(s)."
        else:
            leaderboard += f"\nYou are not on the leaderboard yet. You have {user_po_count} po(s)."

        # Send the leaderboard to the Discord channel
        await ctx.send(leaderboard)

# Function to set up the cog (called when the bot loads this cog)
async def setup(bot):
    await bot.add_cog(Leaderboard(bot))  # Add the cog to the bot