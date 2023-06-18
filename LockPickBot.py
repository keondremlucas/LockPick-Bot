import discord
import logging
from datetime import date, datetime
from datetime import date
import pytz 
import interactions
from discord.ui import Button
from discord.ext import commands
import aiohttp
import requests
import random
TOKEN =  # Replace with your Discord bot Token
API_KEY =   # Replace with your The Odds API key
API_URL = 'https://api.the-odds-api.com/v4/sports/'

# Set the intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


PREDEFINED_SPORTS = ['americanfootball_nfl', 'baseball_mlb', 'basketball_euroleague', 'basketball_nba', 
                     'cricket_t20blast', 'esports_lol', 'mma_mixedmartialarts', 'soccer_epl', 
                     'soccer_uefa_champs_league', 'tennis_atp_singles']

# Opening Menu Buttons/View
class MyButton(discord.ui.Button):
    def __init__(self, label: str, **kwargs):
        super().__init__(label=label, **kwargs)

    async def callback(self, interaction):
        # Define what happens when the button is clicked
        await interaction.followup(f'Button {self.label} clicked!')
        
class MyView(discord.ui.View):
    def __init__(self, array_of_strings):
        super().__init__()
        for string in array_of_strings:
            self.add_item(MyButton(label=string))
            
#Sports Selection Menu/Buttons/View
class SportButton(discord.ui.Button):
    def __init__(self, sport: str,key: str, **kwargs):
        super().__init__(label=sport,custom_id=key, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        sport = self.label
        key = self.custom_id
        keys = key.split('|')
        view = OddsView(keys)
        await interaction.response.send_message('Select:', view=view)
        
class SportView(discord.ui.View):
    def __init__(self, sports: list[str],keys: list[str]):
        super().__init__()
        index = 0
        print('--------')
        print(keys)
        
        for sport in sports:
            if sport == 'Tennis':
                key = 'tennis_atp_french_open|tennis_wta_french_open'
            elif sport == 'Basketball':
                key = 'basketball_nba|basketball_wnba'
            elif sport == 'American Football':
                key = 'americanfootball_nfl|americanfootball_ncaa'
            elif sport == 'Soccer':
                key = 'soccer_uefa_europa|soccer_uefa_nations|soccer_uefa_champs|soccer_usa_mls'
            elif sport == 'Ice Hockey':
                key = 'icehockey_nfl'
            elif sport == 'Mixed Martial Arts':
                key = 'mma_mixed_martial_arts'
            else:
                key = str(random.randint(0,100))
            self.add_item(SportButton(sport,key))
            
class OddsView(discord.ui.View):
    def __init__(self,keys: list[str]):
        super().__init__()
        for key in keys:
            self.add_item(OddsButton(key))
            
class OddsButton(discord.ui.Button):
    def __init__(self, key: str, **kwargs):
        super().__init__(label=key,custom_id=key+'1', **kwargs)
        if self.label == 'tennis_atp_french_open':
                self.label = 'Mens Tennis'
                key = 'tennis_atp_french_open'
        elif self.label == 'basketball_nba':
                self.label = 'NBA Basketball'
        elif self.label == 'basketball_wnba':
                self.label = 'WNBA Basketball'
        elif self.label == 'americanfootball_ncaa':
                self.label = 'College Football'
        elif self.label == 'americanfootball_nfl':
                self.label = 'NFL Football'
        elif self.label == 'mma_mixed_martial_arts':
                self.label = 'MMA'
        else:
                self.label = 'Womens Tennis'
                key = 'tennis_wta_french_open'
    async def callback(self, interaction: discord.Interaction):
            key = [self.custom_id[:-1]]
            if key == ['americanfootball_ncaa']:
                key = ['americanfootball_ncaaf']
            print('-----')
            print(key)
            async with aiohttp.ClientSession() as session:
                url = f"https://api.the-odds-api.com/v4/sports/{key[0]}/odds/?apiKey={API_KEY}&regions=us"
                async with session.get(url) as resp:
                    data = await resp.json()
                    print('-----')
                    print(data)
                    print('----')
                    if not data:
                        await interaction.response.send_message("No data available for this sport. Please try again.")
                        return
            # Parsing commence_time to datetime and adding it as a key
            for game in data:
                game['commence_time_datetime'] = datetime.fromisoformat(game['commence_time'].replace("Z", "+00:00"))

            # Filter out games not commencing today
            data = [game for game in data if game['commence_time_datetime'].date() == date.today()]
            if data.count == 0:
                await interaction.response.send_message("No Events Today")
                return
                
            message = ''
            for game in data:
                message += f"Home Team: {game['home_team']}\nAway Team: {game['away_team']}\n\n"
            for bookmaker in game['bookmakers']:
                message += f"Bookmaker: {bookmaker['title']}\n"
                for market in bookmaker['markets']:
                    for outcome in market['outcomes']:
                        message += f"Outcome: {outcome['name']}\nPrice: {outcome['price']}\n"
                    message += '\n'
                message += '\n'
            if message == '':
                await interaction.response.send_message("No Events Today")
                return
            else:
                await interaction.response.send_message(message)
                return

            

class BetsView(discord.ui.View):
    def __init_(self,  key:list[str], interaction: discord.Interaction):
        super().__init__()
        url = f"https://api.the-odds-api.com/v4/sports/{key[0]}/odds/?apiKey={API_KEY}&regions=us"
        response = requests.get(url)
        data =  response.json()
        print('-----')
        print(data)
        print('----')
        print(odds_data)
        odds_data = data.get('data')
        if not odds_data:
            interaction.response.send_message("No data available for this sport. Please try again.")

        for game in odds_data:
            embed = discord.Embed(title=f"{game['teams'][0]} vs {game['teams'][1]}")
            for site in game['sites']:
                odds = site['odds']['h2h']
                embed.add_field(name=site['site_nice'], value=f"{game['teams'][0]}: {odds[0]}\n{game['teams'][1]}: {odds[1]}", inline=True)
            interaction.followup.send(embed=embed)
    # message = ''
    # for game in data:
    #     message += f"Home Team: {game['home_team']}\nAway Team: {game['away_team']}\n\n"
        
    #     for bookmaker in game['bookmakers']:
    #         message += f"Bookmaker: {bookmaker['title']}\n"
    #         for market in bookmaker['markets']:
    #             for outcome in market['outcomes']:
    #                 message += f"Outcome: {outcome['name']}\nPrice: {outcome['price']}\n"
    #             message += '\n'
    #         message += '\n'
    #     for message in messages:
    #     await ctx.send(content=message)
        
                   
@bot.command()
async def getOdds(ctx: commands.Context):
     async with aiohttp.ClientSession() as session:
        url = f"https://api.the-odds-api.com/v4/sports/?apiKey=APIKEY&regions=us"
        async with session.get(url) as resp:
            data = await resp.json()
            print(data)
        sports = [sport['group'] for sport in data]
        keys = [sport['key'] for sport in data]
        sports = [*set(sports)]
        keys = [*set(keys)]
        
        print(sports)
        print('-------------')
        print(keys)
        view = SportView(sports,keys)
        await ctx.send('Select a sport:', view=view)

   
@bot.command()
async def odds(ctx, sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey=APIKEY&regions=us"
    print(url)
    response = requests.get(url)
     # Error handling for the API request
    if response.status_code != 200:
        print(response.json)
        await ctx.send('Error retrieving odds, please check your input and try again.')
        return
    
    odds_data = response.json()
    print(odds_data)
    
    if not odds_data:
        await ctx.send("No data available for this sport. Please try again.")
        return
    
    message = ''
    for game in odds_data:
        message = f"Home Team: {game['home_team']}\nAway Team: {game['away_team']}\n\n"
        
        for bookmaker in game['bookmakers']:
            message += f"Bookmaker: {bookmaker['title']}\n"
            for market in bookmaker['markets']:
                for outcome in market['outcomes']:
                    message += f"Outcome: {outcome['name']}\nPrice: {outcome['price']}\n"
                message += '\n'
            message += '\n'
        
        await ctx.send(message)

bot.run(TOKEN)