# Discord Bot: Po Counter

This is a Discord bot that tracks the number of times users say "po" in a specified channel.

### To-do list
1. Add achievements/titles you can gain by sending po's.
2. Admin permissions like not having the leaderboard user limit or being able to shut down/restart or make it recount all the po's the bot via a command in discord
3. Add a po shop where polectors can trade in their po counts for items

## Install guide

### Prerequisites
1. Install Python (3.11).
2. Ensure `pip` is installed.
https://pip.pypa.io/en/stable/installation/

### Setup Instructions
1. Clone or download this repository.
2. Navigate to the project folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
4. add your bot token and channel ID to the .env file.
5. run the bot:
   ```bash
   python po.py

### Important
Make sure the bot has the following permissions: send messages, read messages and view channels.
If it is missing any of these permissions the bot might not work as intended.