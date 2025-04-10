# Discord Invite Tracker

## Overview

The **Discord Invite Tracker** is a powerful bot designed to monitor and manage invite links within a Discord server. It tracks invite usage, records who was invited, and provides detailed statistics on invites created by users. This application showcases my expertise in building scalable and maintainable applications using Python and Discord's API.

## Features

- **Invite Tracking**: Monitors invites created in the server and tracks their usage.
- **User Statistics**: Provides detailed statistics on invites created by users, including the number of uses and the users invited.
- **Slash Commands**: Utilizes Discord's slash commands for easy interaction.
- **Data Persistence**: Saves invite data in a JSON file for easy retrieval and management.

## Technologies Used

- **Python**: The primary programming language for the bot.
- **Discord.py**: A powerful library for interacting with the Discord API.
- **dotenv**: For managing environment variables securely.
- **JSON**: For data storage and retrieval.
- **Git**: For version control.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.12 or higher
- pip (Python package installer)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/discord-invite-tracker.git
   cd discord-invite-tracker
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add your Discord bot token:
   ```plaintext
   DISCORD_TOKEN=your_discord_bot_token
   INVITES_FILE=invites.json
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

## Usage

Once the bot is running, you can use the following commands in your Discord server:

- **/createinvite**: Create a new invite link for a specified user.
- **/invites**: Show invite statistics for a user.
- **/detailed-invites**: Show detailed invite statistics, including invited users.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.
