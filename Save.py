import discord
import logging
from interactions import InteractionBot, OptionType, ButtonStyle, ActionRow, Button, ComponentContext
from discord.ext import commands
import requests

TOKEN = 'MTExMTgzNzAzMjIxMDI1NTg5Mg.G2iYmL.D1RqHQeSLhbxO4p7GbVvXgq_7UzxxdrseLOXaY'  # Replace with your Discord bot Token
API_KEY = 'aae20fe489b352655e5fcacbba53f140'  # Replace with your The Odds API key

# Set the intents
intents = discord.Intents.all()
bot = InteractionBot(
    token=TOKEN,
    prefix="!",
    intents = intents
)

PREDEFINED_SPORTS = ['americanfootball_nfl', 'baseball_mlb', 'basketball_euroleague', 'basketball_nba', 
                     'cricket_t20blast', 'esports_lol', 'mma_mixedmartialarts', 'soccer_epl', 
                     'soccer_uefa_champs_league', 'tennis_atp_singles']

def fetch_odds(sport: str):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={API_KEY}&regions=us"
    response = requests.get(url)
    return response.json()

def format_odds_data(odds_data):
    messages = []
    for game in odds_data:
        message = f"Home Team: {game['home_team']}\nAway Team: {game['away_team']}\n\n"
        for bookmaker in game['bookmakers']:
            message += f"Bookmaker: {bookmaker['title']}\n"
            for market in bookmaker['markets']:
                for outcome in market['outcomes']:
                    message += f"Outcome: {outcome['name']}\nPrice: {outcome['price']}\n"
                message += '\n'
            message += '\n'
        messages.append(message)
    return messages

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command()
async def odds(ctx: commands.Context):
    buttons = [
        Button(style=ButtonStyle.GREEN, label=sport, custom_id=sport) for sport in PREDEFINED_SPORTS
    ]
    action_row = ActionRow(*buttons)
    await ctx.send("Please select a sport:", components=[action_row])

@bot.component()
async def on_button_click(ctx: ComponentContext):
    sport = ctx.custom_id
    odds_data = fetch_odds(sport)
    messages = format_odds_data(odds_data)
    for message in messages:
        await ctx.send(content=message)

bot.run(TOKEN)